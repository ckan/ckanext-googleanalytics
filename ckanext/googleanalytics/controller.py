from datetime import datetime
from datetime import timedelta
from pylons import config, request
from beaker import cache
from ckan.lib.base import *
from ckan.authz import Authorizer
from gdata.analytics import client
from ckan import model
from ckanext.googleanalytics import GoogleAnalyticsException

PACKAGE_URL = '/package/'  # XXX get from routes...


class GAController(BaseController):
    def view(self):
        # get package objects corresponding to popular GA content
        c.top_packages = self.get_top_packages()
        return render('index.html')

    def __str__(self):
        # XXX hack to provide consistent cache key; what's the
        # canonical way of doing caching like this in CKAN right now?
        return "analyticscontroller"

    def get_top_packages(self):
        packages_data = self._get_ga_data()
        items = []
        authorizer = Authorizer()
        q = authorizer.authorized_query(None, model.Package)
        for package, visits in packages_data[:10]:
            url_frag = package[len(PACKAGE_URL):]
            if "/" in url_frag:
                continue
            item = q.filter("name = '%s'" % url_frag)
            if not item.count():
                continue
            items.append((item.first(), visits))
        return items

    @cache.cache(expire=3600)
    def _get_ga_data(self):
        SOURCE_APP_NAME = "CKAN Google Analytics Plugin"
        username = config.get('googleanalytics.username')
        password = config.get('googleanalytics.password')
        profile_name = config.get('googleanalytics.profile_name')
        my_client = client.AnalyticsClient(source=SOURCE_APP_NAME)
        my_client.ClientLogin(username,
                              password,
                              SOURCE_APP_NAME)
        account_query = client.AccountFeedQuery({'max-results': '300'})
        feed = my_client.GetAccountFeed(account_query)
        table_id = None
        for entry in feed.entry:
            if entry.title.text == profile_name:
                table_id = entry.table_id.text
                break
        if not table_id:
            msg = "Couldn't find a profile called '%s'" % profile_name
            raise GoogleAnalyticsException(msg)
        now = datetime.now()
        to_date = now.strftime("%Y-%m-%d")
        from_date = now - timedelta(14)
        from_date = from_date.strftime("%Y-%m-%d")
        query = client.DataFeedQuery({'ids': '%s' % table_id,
                                      'start-date': from_date,
                                      'end-date': to_date,
                                      'dimensions': 'ga:source,ga:medium,ga:pagePath',
                                      'metrics': 'ga:visits,ga:visitors,ga:newVisits',
                                      'sort': '-ga:newVisits',
                                      'filters': 'ga:pagePath=~^%s' % PACKAGE_URL,
                                      'max-results': '50'
                                      })
        feed = my_client.GetDataFeed(query)
        packages = []
        for entry in feed.entry:
            for dim in entry.dimension:
                if dim.name == "ga:pagePath":
                    package = dim.value
                    newVisits = entry.get_metric('ga:visits').value
                    packages.append((package, newVisits))
        return packages
