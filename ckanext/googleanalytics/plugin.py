import ast
import logging
import urllib
import commands
import paste.deploy.converters as converters
from ckan.lib.base import c
import ckan.lib.helpers as h
import ckan.plugins as p
from routes.mapper import SubMapper
from pylons import config
from ckan.controllers.package import PackageController

import urllib2
import importlib
import hashlib

import threading
import Queue

log = logging.getLogger('ckanext.googleanalytics')


def _post_analytics(
        user, event_type, request_obj_type, request_function, request_id):

    if config.get('googleanalytics.id'):
        data_dict = {
            "v": 1,
            "tid": config.get('googleanalytics.id'),
            "cid": hashlib.md5(c.user).hexdigest(),
            # customer id should be obfuscated
            "t": "event",
            "dh": c.environ['HTTP_HOST'],
            "dp": c.environ['PATH_INFO'],
            "dr": c.environ.get('HTTP_REFERER', ''),
            "ec": event_type,
            "ea": request_obj_type + request_function,
            "el": request_id,
        }
        GoogleAnalyticsPlugin.analytics_queue.put(data_dict)


def wrap_resource_download(func):

    def func_wrapper(cls, id, resource_id, filename=None):
        _post_analytics(
            c.user,
            "CKAN Resource Download Request",
            "Resource",
            "Download",
            resource_id
        )

        return func(cls, id, resource_id, filename=None)

    return func_wrapper


class GoogleAnalyticsException(Exception):
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


class GoogleAnalyticsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IRoutes, inherit=True)
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

        googleanalytics_linked_domains = config.get(
            'googleanalytics.linked_domains', ''
        )
        self.googleanalytics_linked_domains = [
            x.strip() for x in googleanalytics_linked_domains.split(',') if x
        ]

        if self.googleanalytics_linked_domains:
            self.googleanalytics_fields['allowLinker'] = 'true'

        self.googleanalytics_javascript_url = h.url_for_static(
                '/scripts/ckanext-googleanalytics.js')

        # If resource_prefix is not in config file then write the default value
        # to the config dict, otherwise templates seem to get 'true' when they
        # try to read resource_prefix from config.
        if 'googleanalytics_resource_prefix' not in config:
            config['googleanalytics_resource_prefix'] = (
                    commands.DEFAULT_RESOURCE_URL_TAG)
        self.googleanalytics_resource_prefix = config[
            'googleanalytics_resource_prefix']

        self.show_downloads = converters.asbool(
            config.get('googleanalytics.show_downloads', True))
        self.track_events = converters.asbool(
            config.get('googleanalytics.track_events', False))
        self.enable_user_id = converters.asbool(
            config.get('googleanalytics.enable_user_id', False))

        if not converters.asbool(config.get('ckan.legacy_templates', 'false')):
            p.toolkit.add_resource('fanstatic_library', 'ckanext-googleanalytics')

            # spawn a pool of 5 threads, and pass them queue instance
        for i in range(5):
            t = AnalyticsPostThread(self.analytics_queue)
            t.setDaemon(True)
            t.start()


    def update_config(self, config):
        '''Change the CKAN (Pylons) environment configuration.

        See IConfigurer.

        '''
        if converters.asbool(config.get('ckan.legacy_templates', 'false')):
            p.toolkit.add_template_directory(config, 'legacy_templates')
            p.toolkit.add_public_directory(config, 'legacy_public')
        else:
            p.toolkit.add_template_directory(config, 'templates')

    def before_map(self, map):
        '''Add new routes that this extension's controllers handle.

        See IRoutes.

        '''
        # Helpers to reduce code clutter
        GET = dict(method=['GET'])
        PUT = dict(method=['PUT'])
        POST = dict(method=['POST'])
        DELETE = dict(method=['DELETE'])
        GET_POST = dict(method=['GET', 'POST'])
        # intercept API calls that we want to capture analytics on
        register_list = [
            'package',
            'dataset',
            'resource',
            'tag',
            'group',
            'related',
            'revision',
            'licenses',
            'rating',
            'user',
            'activity'
        ]
        register_list_str = '|'.join(register_list)
        # /api ver 3 or none
        with SubMapper(map, controller='ckanext.googleanalytics.controller:GAApiController', path_prefix='/api{ver:/3|}',
                    ver='/3') as m:
            m.connect('/action/{logic_function}', action='action',
                      conditions=GET_POST)

        # /api ver 1, 2, 3 or none
        with SubMapper(map, controller='ckanext.googleanalytics.controller:GAApiController', path_prefix='/api{ver:/1|/2|/3|}',
                       ver='/1') as m:
            m.connect('/search/{register}', action='search')

        # /api/rest ver 1, 2 or none
        with SubMapper(map, controller='ckanext.googleanalytics.controller:GAApiController', path_prefix='/api{ver:/1|/2|}',
                       ver='/1', requirements=dict(register=register_list_str)
                       ) as m:

            m.connect('/rest/{register}', action='list', conditions=GET)
            m.connect('/rest/{register}', action='create', conditions=POST)
            m.connect('/rest/{register}/{id}', action='show', conditions=GET)
            m.connect('/rest/{register}/{id}', action='update', conditions=PUT)
            m.connect('/rest/{register}/{id}', action='update', conditions=POST)
            m.connect('/rest/{register}/{id}', action='delete', conditions=DELETE)

        return map

    def after_map(self, map):
        '''Add new routes that this extension's controllers handle.

        See IRoutes.

        '''
        self.modify_resource_download_route(map)
        map.redirect("/analytics/package/top", "/analytics/dataset/top")
        map.connect(
            'analytics', '/analytics/dataset/top',
            controller='ckanext.googleanalytics.controller:GAController',
            action='view'
        )
        return map

    def get_helpers(self):
        '''Return the CKAN 2.0 template helper functions this plugin provides.

        See ITemplateHelpers.

        '''
        return {'googleanalytics_header': self.googleanalytics_header}

    def googleanalytics_header(self):
        '''Render the googleanalytics_header snippet for CKAN 2.0 templates.

        This is a template helper function that renders the
        googleanalytics_header jinja snippet. To be called from the jinja
        templates in this extension, see ITemplateHelpers.

        '''

        if self.enable_user_id and c.user:
            self.googleanalytics_fields['userId'] = str(c.userobj.id)

        data = {
            'googleanalytics_id': self.googleanalytics_id,
            'googleanalytics_domain': self.googleanalytics_domain,
            'googleanalytics_fields': str(self.googleanalytics_fields),
            'googleanalytics_linked_domains': self.googleanalytics_linked_domains
        }
        return p.toolkit.render_snippet(
            'googleanalytics/snippets/googleanalytics_header.html', data)

    def modify_resource_download_route(self, map):
        '''Modifies resource_download method in related controller
        to attach GA tracking code.
        '''

        if '_routenames' in map.__dict__:
            if 'resource_download' in map.__dict__['_routenames']:
                route_data = map.__dict__['_routenames']['resource_download'].__dict__
                route_controller = route_data['defaults']['controller'].split(
                    ':')
                module = importlib.import_module(route_controller[0])
                controller_class = getattr(module, route_controller[1])
                controller_class.resource_download = wrap_resource_download(
                    controller_class.resource_download)
            else:
                # If no custom uploader applied, use the default one
                PackageController.resource_download = wrap_resource_download(
                    PackageController.resource_download)
