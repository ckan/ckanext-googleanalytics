# -*- coding: utf-8 -*-
import queue

import ckan.plugins as plugins

from ckanext.googleanalytics.views import ga
from ckanext.googleanalytics.cli import get_commands


class GAMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    analytics_queue = queue.Queue()

    # IBlueprint

    def get_blueprint(self):
        return [ga]

    # IClick

    def get_commands(self):
        return get_commands()
