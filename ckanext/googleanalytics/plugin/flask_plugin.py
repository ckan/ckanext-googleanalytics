# -*- coding: utf-8 -*-
from future import standard_library

standard_library.install_aliases()
import queue

import ckan.plugins as plugins

from ckanext.googleanalytics.views import ga


class GAMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)

    analytics_queue = queue.Queue()

    # IBlueprint

    def get_blueprint(self):
        return [ga]
