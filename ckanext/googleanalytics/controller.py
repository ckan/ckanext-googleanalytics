import logging
from ckan.lib.base import *
import dbutil


log = logging.getLogger('ckanext.googleanalytics')


class GAController(BaseController):
    def view(self):
        # get package objects corresponding to popular GA content
        self.parse_ga_data()
        c.top_packages = self.get_top_packages()
        return render('index.html')

    def __str__(self):
        # XXX hack to provide consistent cache key; what's the
        # canonical way of doing caching like this in CKAN right now?
        return "analyticscontroller"

    def get_top_packages(self):
        items = dbutil.get_top_packages()
        return items
