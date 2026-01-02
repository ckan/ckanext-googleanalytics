# Copyright (C) 2022 Entidad Pública Empresarial Red.es
#
# This file is part of "dge_ga (datos.gob.es)".
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import ast
import logging
import urllib
import paste.deploy.converters as converters
import pylons
import ckan.lib.helpers as h
import ckan.plugins as p

import urllib2

import threading
import Queue

log = logging.getLogger('ckanext.dge_ga')
DEFAULT_RESOURCE_URL_TAG = '/downloads/'

class DgeGAException(Exception):
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

            data = urllib.urlencode(data_dict)
            log.debug("Sending API event to Google Analytics: " + data)
            # send analytics
            urllib2.urlopen(
                "http://www.google-analytics.com/collect",
                data,
                # timeout in seconds
                # https://docs.python.org/2/library/urllib2.html#urllib2.urlopen
                10)

            # signals to queue job is done
            self.queue.task_done()


class DgeGaPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers)

    analytics_queue = Queue.Queue()

    def configure(self, config):
        '''Load config settings for this extension from config file.

        See IConfigurable.

        '''
        if 'googleanalytics.id' not in config:
            msg = "Missing googleanalytics.id in config"
            raise GoogleAnalyticsException(msg)
        self.googleanalytics_id = config['googleanalytics.id']
        self.googleanalytics_domain = config.get(
                'googleanalytics.domain', 'auto')
        self.googleanalytics_fields = ast.literal_eval(config.get(
            'googleanalytics.fields', '{}'))
        self.googleanalytics_javascript_url = h.url_for_static(
                '/scripts/ckanext-googleanalytics.js')

        # If resource_prefix is not in config file then write the default value
        # to the config dict, otherwise templates seem to get 'true' when they
        # try to read resource_prefix from config.
        if 'googleanalytics_resource_prefix' not in config:
            config['googleanalytics_resource_prefix'] = (DEFAULT_RESOURCE_URL_TAG)
        self.googleanalytics_resource_prefix = config[
            'googleanalytics_resource_prefix']

        self.show_downloads = converters.asbool(
            config.get('googleanalytics.show_downloads', True))
        self.track_events = converters.asbool(
            config.get('googleanalytics.track_events', False))

        self.ga_send_stats = converters.asbool(config.get('ckanext.dge_ga.send_stats', True))

        log.debug('ga_send_stats=%s', self.ga_send_stats)
        p.toolkit.add_resource('fanstatic_library', 'ckanext-dge-ga')

            # spawn a pool of 5 threads, and pass them queue instance
        for i in range(5):
            t = AnalyticsPostThread(self.analytics_queue)
            t.setDaemon(True)
            t.start()


    def update_config(self, config):
        '''Change the CKAN (Pylons) environment configuration.

        See IConfigurer.

        '''
        p.toolkit.add_template_directory(config, 'templates')


    def get_helpers(self):
        '''Return the CKAN 2.0 template helper functions this plugin provides.

        See ITemplateHelpers.

        '''
        return {'dge_ga_googleanalytics_header': self.dge_ga_googleanalytics_header,
                'dge_ga_send_stats': self.dge_ga_send_stats}

    def dge_ga_googleanalytics_header(self):
        '''Render the googleanalytics_header snippet for CKAN 2.0 templates.

        This is a template helper function that renders the
        googleanalytics_header jinja snippet. To be called from the jinja
        templates in this extension, see ITemplateHelpers.

        '''
        data = {'googleanalytics_id': self.googleanalytics_id,
                'googleanalytics_domain': self.googleanalytics_domain,
                'googleanalytics_fields': str(self.googleanalytics_fields)}
        return p.toolkit.render_snippet(
                'googleanalytics/snippets/dge_ga_header.html', data)
    
    def dge_ga_send_stats(self):
        return self.ga_send_stats
