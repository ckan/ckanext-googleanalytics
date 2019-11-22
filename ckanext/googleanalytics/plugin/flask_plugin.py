# -*- coding: utf-8 -*-
import Queue

import ckan.plugins as plugins

from ckanext.googleanalytics.views import ga


class GAMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)

    analytics_queue = Queue.Queue()

    def get_blueprint(self):
        return [ga]
