import logging
import urllib
from paste.deploy.converters import asbool
from genshi.filters import Transformer
from genshi import HTML
from genshi.core import START, TEXT
from genshi.filters.transform import INSIDE, EXIT
from pylons import config, request
import ckan.plugins as p
import gasnippet
import commands
import dbutil

log = logging.getLogger('ckanext.googleanalytics')


class GoogleAnalyticsException(Exception):
    pass


class GoogleAnalyticsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IGenshiStreamFilter, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

    def configure(self, config):
        self.config = config
        if (not 'googleanalytics.id' in config):
            msg = "Missing googleanalytics.id in config"
            raise GoogleAnalyticsException(msg)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')

    def after_map(self, map):
        map.redirect("/analytics/package/top", "/analytics/dataset/top")
        map.connect('analytics', '/analytics/dataset/top',
                    controller='ckanext.googleanalytics.controller:GAController',
                    action='view')
        return map

    def filter(self, stream):
        log.info("Inserting GA code into template")
        ga_id = self.config['googleanalytics.id']
        ga_domain = self.config.get('googleanalytics.domain', 'auto')
        code = HTML(gasnippet.gacode % (ga_id, ga_domain))
        stream = stream | Transformer('head').append(code)
        resource_url = config.get('googleanalytics.resource_prefix',
                                  commands.DEFAULT_RESOURCE_URL_TAG)

        routes = request.environ.get('pylons.routes_dict')
        action = routes.get('action')
        controller = routes.get('controller')
        if (controller == 'package' and \
            action in ['search', 'read', 'resource_read']) or \
            (controller == 'group' and action == 'read'):

            log.info("Tracking of resource downloads")
            show_downloads = (
                asbool(config.get('googleanalytics.show_downloads', True)) and
                action == 'read' and controller == 'package'
            )

            # add download tracking link
            def js_attr(name, event):
                attrs = event[1][1]
                href = attrs.get('href').encode('utf-8')
                link = '%s%s' % (resource_url, urllib.quote(href))
                js = "javascript: _gaq.push(['_trackPageview', '%s']);" % link
                return js

            # add some stats
            def download_adder(stream):
                download_html = '''<span class="downloads-count">
                [downloaded %s times]</span>'''
                count = None
                for mark, (kind, data, pos) in stream:
                    if mark and kind == START:
                        href = data[1].get('href')
                        if href:
                            count = dbutil.get_resource_visits_for_url(href)
                    if count and mark is EXIT:
                        # emit count
                        yield INSIDE, (TEXT, HTML(download_html % count), pos)
                    yield mark, (kind, data, pos)

            # and some styling
            download_style = '''
            <style type="text/css">
               span.downloads-count {
               font-size: 0.9em;
               }
            </style>
            '''

            # perform the stream transform
            stream = stream | Transformer('//a[contains(@class, "resource-url-analytics")]')\
                .attr('onclick', js_attr)

            if show_downloads:
                stream = stream | Transformer('//a[contains(@class, "resource-url-analytics")]')\
                    .apply(download_adder)
                stream = stream | Transformer('//head').append(HTML(download_style))

        return stream
