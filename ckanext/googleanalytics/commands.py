import logging
import datetime
import time

from pylons import config as pylonsconfig
from ckan.lib.cli import CkanCommand
from gdata.analytics import client
import ckan.model as model

import dbutil

log = logging.getLogger('ckanext.googleanalytics')
PACKAGE_URL = '/dataset/'  # XXX get from routes...
DEFAULT_RESOURCE_URL_TAG = '/downloads/'


class InitDB(CkanCommand):
    """Initialise the local stats database tables
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()
        # funny dance we need to do to make sure we've got a
        # configured session
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)
        dbutil.init_tables()
        log.info("Set up statistics tables in main database")


class LoadAnalytics(CkanCommand):
    """Parse data from Google Analytics API and store it
    in a local database

    Options:
        internal [date] use ckan internal tracking tables
                        date specifies start date for retrieving
                        analytics data YYYY-MM-DD format
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 2
    min_args = 0
    TEST_HOST = None
    CONFIG = None

    def command(self):
        if not self.CONFIG:
            self._load_config()
            self.CONFIG = pylonsconfig

        self.resource_url_tag = self.CONFIG.get(
            'googleanalytics.resource_prefix',
            DEFAULT_RESOURCE_URL_TAG)
        self.setup_ga_connection()
        # funny dance we need to do to make sure we've got a
        # configured session
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)
        self.parse_and_save()

    def internal_save(self, packages_data, summary_date):
        engine = model.meta.engine
        # clear out existing data before adding new
        sql = '''DELETE FROM tracking_summary
                 WHERE tracking_date='%s'; ''' % summary_date
        engine.execute(sql)

        for url, count in packages_data.iteritems():
            if url.startswith(DEFAULT_RESOURCE_URL_TAG):
                tracking_type = 'resource'
                # remove the leading identifier
                url = url[len(DEFAULT_RESOURCE_URL_TAG):]
            else:
                tracking_type = 'page'

            sql = '''INSERT INTO tracking_summary
                     (url, count, tracking_date, tracking_type)
                     VALUES (%s, %s, %s, %s);'''
            engine.execute(sql, url, count, summary_date, tracking_type)

        # get ids for dataset urls
        sql = '''UPDATE tracking_summary t
                 SET package_id = COALESCE(
                     (SELECT id FROM package p WHERE t.url =  %s || p.name)
                     ,'~~not~found~~')
                 WHERE t.package_id IS NULL AND tracking_type = 'page';'''
        engine.execute(sql, PACKAGE_URL)

        # update summary totals for resources
        sql = '''UPDATE tracking_summary t1
                 SET running_total = (
                    SELECT sum(count)
                    FROM tracking_summary t2
                    WHERE t1.url = t2.url
                    AND t2.tracking_date <= t1.tracking_date
                 ) + t1.count
                 ,recent_views = (
                    SELECT sum(count)
                    FROM tracking_summary t2
                    WHERE t1.url = t2.url
                    AND t2.tracking_date <= t1.tracking_date AND t2.tracking_date >= t1.tracking_date - 14
                 ) + t1.count
                 WHERE t1.running_total = 0 AND tracking_type = 'resource';'''
        engine.execute(sql)

        # update summary totals for pages
        sql = '''UPDATE tracking_summary t1
                 SET running_total = (
                    SELECT sum(count)
                    FROM tracking_summary t2
                    WHERE t1.package_id = t2.package_id
                    AND t2.tracking_date <= t1.tracking_date
                 ) + t1.count
                 ,recent_views = (
                    SELECT sum(count)
                    FROM tracking_summary t2
                    WHERE t1.package_id = t2.package_id
                    AND t2.tracking_date <= t1.tracking_date AND t2.tracking_date >= t1.tracking_date - 14
                 ) + t1.count
                 WHERE t1.running_total = 0 AND tracking_type = 'page'
                 AND t1.package_id IS NOT NULL
                 AND t1.package_id != '~~not~found~~';'''
        engine.execute(sql)

    def bulk_import(self):
        if len(self.args) == 2:
            # Get summeries from specified date
            start_date = datetime.datetime.strptime(self.args[1], '%Y-%m-%d')
        else:
            # No date given. See when we last have data for and get data
            # from 2 days before then in case new data is available.
            # If no date here then use 2010-01-01 as the start date
            engine = model.meta.engine
            sql = '''SELECT tracking_date from tracking_summary
                     ORDER BY tracking_date DESC LIMIT 1;'''
            result = engine.execute(sql).fetchall()
            if result:
                start_date = result[0]['tracking_date']
                start_date += datetime.timedelta(-2)
                # convert date to datetime
                combine = datetime.datetime.combine
                start_date = combine(start_date, datetime.time(0))
            else:
                start_date = datetime.datetime(2011, 1, 1)
        end_date = datetime.datetime.now()
        while start_date < end_date:
            stop_date = start_date + datetime.timedelta(1)
            packages_data = self.get_ga_data_new(start_date=start_date,
                                                 end_date=stop_date)
            self.internal_save(packages_data, start_date)
            # sleep to rate limit requests
            time.sleep(0.25)
            start_date = stop_date
            log.info('%s recieved %s' % (len(packages_data), start_date))
            print '%s recieved %s' % (len(packages_data), start_date)

    def get_ga_data_new(self, start_date=None, end_date=None):
        """Get raw data from Google Analtyics for packages and
        resources.

        Returns a dictionary like::

           {'identifier': 3}
        """
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        packages = {}
        query = 'ga:pagePath=~^%s,ga:pagePath=~^%s' % \
                    (PACKAGE_URL, self.resource_url_tag)
        metrics = 'ga:uniquePageviews'
        sort = '-ga:uniquePageviews'

        start_index = 1
        max_results = 10000
        # data retrival is chunked
        while True:
            feed = self.ga_query(query_filter=query,
                                 from_date=start_date,
                                 start_index=start_index,
                                 max_results=max_results,
                                 metrics=metrics,
                                 sort=sort,
                                 to_date=end_date)
            for entry in feed.entry:
                for dim in entry.dimension:
                    if dim.name == "ga:pagePath":
                        package = dim.value
                        count = entry.get_metric(
                            'ga:uniquePageviews').value or 0
                        packages[package] = int(count)
            if len(feed.entry) < max_results:
                break
            start_index += max_results
            # rate limiting
            time.sleep(0.25)
        return packages

    def parse_and_save(self):
        """Grab raw data from Google Analytics and save to the database"""
        if len(self.args):
            if self.args[0].lower() != 'internal':
                raise Exception('Illegal argument %s' % self.args[0])
            self.bulk_import()
        else:
            packages_data = self.get_ga_data()
            self.save_ga_data(packages_data)
            log.info("Saved %s records from google" % len(packages_data))

    def save_ga_data(self, packages_data):
        """Save tuples of packages_data to the database
        """
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
        my_client.ClientLogin(username, password, SOURCE_APP_NAME)
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

    def ga_query(self, query_filter=None, from_date=None, to_date=None,
                 start_index=1, max_results=10000, metrics=None, sort=None):
        """Execute a query against Google Analytics
        """
        if not to_date:
            now = datetime.datetime.now()
            to_date = now.strftime("%Y-%m-%d")
        if not metrics:
            metrics = 'ga:visits,ga:visitors,ga:newVisits,ga:uniquePageviews'
        if not sort:
            sort = '-ga:newVisits'
        query = client.DataFeedQuery({'ids': '%s' % self.table_id,
                                      'start-date': from_date,
                                      'end-date': to_date,
                                      'dimensions': 'ga:pagePath',
                                      'metrics': metrics,
                                      'sort': sort,
                                      'start-index': start_index,
                                      'filters': query_filter,
                                      'max-results': max_results
                                      })
        feed = self.client.GetDataFeed(query)
        return feed

    def get_ga_data(self, query_filter=None, start_date=None, end_date=None):
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

