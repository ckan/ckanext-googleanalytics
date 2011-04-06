import logging
import urllib
import os
from paste.deploy.converters import asbool
from genshi.filters import Transformer
from genshi import HTML
from genshi.core import START, TEXT, END
from genshi.filters.transform import INSIDE, EXIT
from pylons import config
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IGenshiStreamFilter, IConfigurable, IRoutes
from ckan.plugins import IConfigurer
from gasnippet import gacode
from commands import DEFAULT_RESOURCE_URL_TAG
import dbutil

log = logging.getLogger('ckanext.googleanalytics')


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
        ga_domain = self.config.get('googleanalytics.domain', 'auto')
        code = HTML(gacode % (ga_id, ga_domain))
        stream = stream | Transformer('head').append(code)
        resource_url = config.get('googleanalytics.resource_prefix',
                                  DEFAULT_RESOURCE_URL_TAG)
        show_downloads = asbool(config.get('googleanalytics.show_downloads',
                                           False))

        # add download tracking link
        def js_attr(name, event):
            attrs = event[1][1]
            link = '%s%s' % (resource_url,
                             urllib.quote(attrs.get('href')))
            js = "javascript: _gaq.push(['_trackPageview', '%s']);" % link
            return js

        # add some stats
        def download_adder(stream):
            download_html = ''' <span class="downloads-count">
            (%s downloads)</span>'''
            count = None
            for mark, (kind, data, pos) in stream:
                if mark and kind == START:
                    href = data[1].get('href')
                    if href:
                        count = dbutil.get_resource_visits_for_url(href)
                if count and mark is EXIT:
                    # emit count
                    yield INSIDE, (TEXT,
                                   HTML(download_html % count),
                                   pos)
                yield mark, (kind, data, pos)

        # perform the stream transform
        stream = stream | Transformer(
            '//div[@id="package"]//td/a')\
            .attr('onclick', js_attr)
        if show_downloads:
            stream = stream | Transformer(
                '//div[@id="package"]//td/a')\
                .apply(download_adder)
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
