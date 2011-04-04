import logging
import urllib

log = logging.getLogger(__name__)
import os
from genshi.filters import Transformer
from genshi import HTML
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IGenshiStreamFilter, IConfigurable, IRoutes
from ckan.plugins import IConfigurer
from ckan import model
from gasnippet import gacode


class GoogleAnalyticsException(Exception):
    pass


class GoogleAnalyticsPlugin(SingletonPlugin):
    implements(IConfigurable, inherit=True)
    implements(IGenshiStreamFilter, inherit=True)
    implements(IRoutes, inherit=True)
    implements(IConfigurer, inherit=True)

    def configure(self, config):
        self.config = config
        log.info("Loading Google Analytics plugin...")
        if (not 'googleanalytics.id' in config):
            msg = "Missing googleanalytics.id in config"
            raise GoogleAnalyticsException(msg)

    def filter(self, stream):
        log.info("Inserting GA code into template")
        ga_id = self.config['googleanalytics.id']
        code = HTML(gacode % ga_id)
        stream = stream | Transformer('head').append(code)

        # add download tracking link
        def js_attr(name, event):
            attrs = event[1][1]
            link = '/downloads/%s' % urllib.quote(attrs.get('href'))
            js = "javascript: _gaq.push(['_trackPageview', '%s']);" % link
            return js
        stream = stream | Transformer(
            '//div[@id="package"]//td/a')\
            .attr('onclick', js_attr)

        return stream

    def after_map(self, map):
        map.connect('analytics', '/analytics/package/top',
                    controller='ckanext.googleanalytics.controller:GAController',
                    action='view')
        return map

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        template_dir = os.path.join(rootdir, 'ckanext',
                                      'googleanalytics', 'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])
