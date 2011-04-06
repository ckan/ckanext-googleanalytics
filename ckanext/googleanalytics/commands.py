import logging
import datetime
from pylons import config as pylonsconfig
from ckan.lib.cli import CkanCommand
from gdata.analytics import client
import ckan.model as model
from sqlalchemy.orm import sessionmaker

import dbutil

log = logging.getLogger('ckanext.googleanalytics')
PACKAGE_URL = '/package/'  # XXX get from routes...
DEFAULT_RESOURCE_URL_TAG = '/downloads/'


class LoadAnalytics(CkanCommand):
    """Parse data from Google Analytics API and store it in a local
    database
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0
    TEST_HOST = None
    CONFIG = pylonsconfig

    def command(self):
        self._load_config()
        self.resource_url_tag = self.CONFIG.get(
            'googleanalytics.resource_prefix',
            DEFAULT_RESOURCE_URL_TAG)
        self.setup_ga_connection()
        # funny dance we need to do to make sure we've got a
        # configured session
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)
        self.parse_and_save()

    def parse_and_save(self):
        """Grab raw data from Google Analytics and save to the
        database
        """
        packages_data = self.get_ga_data()
        self.save_ga_data(packages_data)
        log.info("Saved %s records from google" % len(packages_data))

    def save_ga_data(self, packages_data):
        """Save tuples of packages_data to the database
        """
        dbutil.init_tables()
        for identifier, visits in packages_data.items():
            recently = visits.get('recent', 0)
            ever = visits.get('ever', 0)
            if identifier.startswith(self.resource_url_tag):
                resource_url = identifier[len(self.resource_url_tag):]
                resource = model.Session.query(model.Resource).autoflush(True)\
                           .filter_by(url=resource_url).first()
                if not resource:
                    log.warning("Couldn't find resource %s" % resource_url)
                    continue
                dbutil.update_resource_visits(resource.id, recently, ever)
                log.info("Updated %s with %s visits" % (resource.id, visits))
            else:
                package_name = identifier[len(PACKAGE_URL):]
                if "/" in package_name:
                    log.warning("%s not a valid package name" % package_name)
                    continue
                item = model.Package.by_name(package_name)
                if not item:
                    log.warning("Couldn't find package %s" % package_name)
                    continue
                dbutil.update_package_visits(item.id, recently, ever)
                log.info("Updated %s with %s visits" % (item.id, visits))
        model.Session.commit()

    def setup_ga_connection(self):
        """Log into the Google Data API, and find out the ``table_id``
        that is associated with the profile, for later querying
        """
        SOURCE_APP_NAME = "CKAN Google Analytics Plugin"
        username = self.CONFIG.get('googleanalytics.username')
        password = self.CONFIG.get('googleanalytics.password')
        ga_id = self.CONFIG.get('googleanalytics.id')
        if not username or not password or not ga_id:
            raise Exception("No googleanalytics profile info in config")
        if self.TEST_HOST:
            my_client = client.AnalyticsClient(source=SOURCE_APP_NAME,
                                               http_client=self.TEST_HOST)
        else:
            my_client = client.AnalyticsClient(source=SOURCE_APP_NAME)
        my_client.ClientLogin(username,
                              password,
                              SOURCE_APP_NAME)
        account_query = client.AccountFeedQuery({'max-results': '300'})
        feed = my_client.GetAccountFeed(account_query)
        table_id = None
        for entry in feed.entry:
            if entry.get_property("ga:webPropertyId").value == ga_id:
                table_id = entry.table_id.text
                break
        if not table_id:
            msg = "Couldn't find a profile with id '%s'" % ga_id
            raise Exception(msg)
        self.table_id = table_id
        self.client = my_client

    def ga_query(self, query_filter=None, from_date=None):
        """Executie a query against Google Analytics
        """
        now = datetime.datetime.now()
        to_date = now.strftime("%Y-%m-%d")
        metrics = 'ga:visits,ga:visitors,ga:newVisits,ga:uniquePageviews'
        query = client.DataFeedQuery({'ids': '%s' % self.table_id,
                                      'start-date': from_date,
                                      'end-date': to_date,
                                      'dimensions': 'ga:pagePath',
                                      'metrics': metrics,
                                      'sort': '-ga:newVisits',
                                      'filters': query_filter,
                                      'max-results': '10000'
                                      })
        feed = self.client.GetDataFeed(query)
        return feed

    def get_ga_data(self, query_filter=None):
        """Get raw data from Google Analtyics for packages and
        resources, and for both the last two weeks and ever.

        Returns a dictionary like::

           {'identifier': {'recent':3, 'ever':6}}
        """
        now = datetime.datetime.now()
        recent_date = now - datetime.timedelta(14)
        recent_date = recent_date.strftime("%Y-%m-%d")
        floor_date = datetime.date(2005, 1, 1)
        packages = {}
        queries = ['ga:pagePath=~^%s' % PACKAGE_URL,
                   'ga:pagePath=~^%s' % self.resource_url_tag]
        dates = {'recent': recent_date, 'ever': floor_date}
        for date_name, date in dates.items():
            for query in queries:
                feed = self.ga_query(query_filter=query,
                                     from_date=date)
                for entry in feed.entry:
                    for dim in entry.dimension:
                        if dim.name == "ga:pagePath":
                            package = dim.value
                            count = entry.get_metric(
                                'ga:uniquePageviews').value or 0
                            packages.setdefault(package, {})[date_name] = count
        return packages
