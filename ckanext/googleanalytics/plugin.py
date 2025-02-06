
import logging
import queue
import threading

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.exceptions import CkanConfigurationException

from ckanext.googleanalytics import helpers, utils
from ckanext.googleanalytics.cli import get_commands
from ckanext.googleanalytics.logic import action, auth
from ckanext.googleanalytics.views import ga

log = logging.getLogger(__name__)




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
            data = self.queue.get()
            utils.send_event(data)
            # signals to queue job is done
            self.queue.task_done()


class GoogleAnalyticsPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)

    analytics_queue = queue.Queue()

    # IBlueprint

    def get_blueprint(self):
        return [ga]

    # IClick

    def get_commands(self):
        return get_commands()

    def get_auth_functions(self):
        return auth.get_auth()

    def get_actions(self):
        return action.get_actions()

    def configure(self, config):
        # spawn a pool of 5 threads, and pass them queue instance
        for _i in range(5):
            t = AnalyticsPostThread(self.analytics_queue)
            t.setDaemon(True)
            t.start()

    def update_config(self, config):
        tk.add_template_directory(config, "templates")
        tk.add_resource("assets", "ckanext-googleanalytics")

        if not config.get("googleanalytics.id"):
            msg = "Missing or empty googleanalytics.id in config"
            raise GoogleAnalyticsException(msg)

    def get_helpers(self):
        return helpers.get_helpers()


if tk.check_ckan_version("2.10"):
    tk.blanket.config_declarations(GoogleAnalyticsPlugin)
