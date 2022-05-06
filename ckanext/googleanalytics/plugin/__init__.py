# -*- coding: utf-8 -*-
from __future__ import absolute_import

from six.moves.urllib.parse import urlencode
import logging
import threading

import requests

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckan.exceptions import CkanConfigurationException, CkanVersionException

from ckanext.googleanalytics import helpers

log = logging.getLogger(__name__)

try:
    tk.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.googleanalytics.plugin.pylons_plugin import GAMixinPlugin
else:
    from ckanext.googleanalytics.plugin.flask_plugin import GAMixinPlugin


class GoogleAnalyticsException(CkanConfigurationException):
    pass


class AnalyticsPostThread(threading.Thread):
    """Threaded Url POST"""

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # grabs host from queue
            data_dict = self.queue.get()

            data = urlencode(data_dict)
            log.debug("Sending API event to Google Analytics: " + data)
            # send analytics
            res = requests.post(
                "http://www.google-analytics.com/collect",
                data,
                timeout=10,
            )
            # signals to queue job is done
            self.queue.task_done()


class GoogleAnalyticsPlugin(GAMixinPlugin, p.SingletonPlugin):

    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers)

    def configure(self, config):
        # spawn a pool of 5 threads, and pass them queue instance
        for _i in range(5):
            t = AnalyticsPostThread(self.analytics_queue)
            t.setDaemon(True)
            t.start()

    def update_config(self, config):
        tk.add_template_directory(config, "../templates")
        tk.add_resource("../assets", "ckanext-googleanalytics")

        if "googleanalytics.id" not in config:
            msg = "Missing googleanalytics.id in config"
            raise GoogleAnalyticsException(msg)

    def get_helpers(self):
        return helpers.get_helpers()


if tk.check_ckan_version("2.10"):
    tk.blanket.config_declarations(GoogleAnalyticsPlugin)
