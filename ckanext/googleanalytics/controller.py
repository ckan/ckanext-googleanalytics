from __future__ import absolute_import

import logging
from ckan.lib.base import BaseController, c, render, request
from . import dbutil

import ckan.logic as logic
import hashlib
from . import plugin
from pylons import config

from paste.util.multidict import MultiDict

from ckan.controllers.api import ApiController

from ckan.exceptions import CkanVersionException
import ckan.plugins.toolkit as tk
try:
    tk.requires_ckan_version("2.9")
except CkanVersionException:
    pass
else:
    from builtins import str

import ckan.model as model
from ckan.common import _, c, request, response

log = logging.getLogger("ckanext.googleanalytics")


class GAController(BaseController):
    def view(self):
        # get package objects corresponding to popular GA content
        c.top_resources = dbutil.get_top_resources(limit=10)
        return render("summary.html")


class GAApiController(ApiController):
    # intercept API calls to record via google analytics
    def _post_analytics(
        self, user, request_obj_type, request_function, request_id
    ):
        if config.get("googleanalytics.id"):
            data_dict = {
                "v": 1,
                "tid": config.get("googleanalytics.id"),
                "cid": hashlib.md5(user).hexdigest(),
                # customer id should be obfuscated
                "t": "event",
                "dh": c.environ["HTTP_HOST"],
                "dp": c.environ["PATH_INFO"],
                "dr": c.environ.get("HTTP_REFERER", ""),
                "ec": "CKAN API Request",
                "ea": request_obj_type + request_function,
                "el": request_id,
            }
            context = {'model': model, 'session': model.Session, 'user': c.user,
                       'api_version': None, 'auth_user_obj': c.userobj}
 
            
            '''
            Send GA custom dimension parameter to generate better report. 
                "cd1" : Organization Name 
                "cd2" : Package Name
                "cd3" : Resource Name
            '''
            package_level_action = ['package_show', 'package_patch', 'package_update'
                                    'datastore_search',
                                    ]

            resource_level_action = ['resource_show', 'resource_patch', 'resource_update',
                                     'datastore_search', ' datastore_search_sql',
                                     ]

            if not request_id:
                request_id = {}
            else:
                request_id = {"id": request_id}

            if(request_obj_type in package_level_action):
                pkg = logic.get_action(request_obj_type)(dict(context, return_type='dict'), request_id)
                data_dict.update({
                    "cd1": pkg["organization"]["name"],
                    "cd2": pkg["name"]
                })
            if(request_obj_type in resource_level_action):
                resource = logic.get_action('resource_show')(dict(context, return_type='dict'), request_id)
                pkg = logic.get_action('package_show')(
                    dict(context, return_type='dict'), {'id': resource['package_id']})
                data_dict.update({
                    "cd1": pkg["organization"]["name"],
                    "cd2": pkg["name"],
                    "cd3": resource["name"]
                })   
            plugin.GoogleAnalyticsPlugin.analytics_queue.put(data_dict)

    def action(self, logic_function, ver=None):
        try:
            function = logic.get_action(logic_function)
            side_effect_free = getattr(function, "side_effect_free", False)
            request_data = self._get_request_data(
                try_url_params=side_effect_free
            )
            if isinstance(request_data, dict):
                if request_data.get("id", False):
                    id = request_data.get("id")
                else: 
                    id = request_data.get("resource_id")

                if "q" in request_data:
                    id = request_data["q"]
                if "query" in request_data:
                    id = request_data["query"]
                self._post_analytics(c.user, logic_function, "", id)
        except Exception as e:
            log.debug(e)
            pass
        return ApiController.action(self, logic_function, ver)

    def list(self, ver=None, register=None, subregister=None, id=None):
        self._post_analytics(
            c.user,
            register + ("_" + str(subregister) if subregister else ""),
            "list",
            id,
        )
        return ApiController.list(self, ver, register, subregister, id)

    def show(
        self, ver=None, register=None, subregister=None, id=None, id2=None
    ):
        self._post_analytics(
            c.user,
            register + ("_" + str(subregister) if subregister else ""),
            "show",
            id,
        )
        return ApiController.show(self, ver, register, subregister, id, id2)

    def update(
        self, ver=None, register=None, subregister=None, id=None, id2=None
    ):
        self._post_analytics(
            c.user,
            register + ("_" + str(subregister) if subregister else ""),
            "update",
            id,
        )
        return ApiController.update(self, ver, register, subregister, id, id2)

    def delete(
        self, ver=None, register=None, subregister=None, id=None, id2=None
    ):
        self._post_analytics(
            c.user,
            register + ("_" + str(subregister) if subregister else ""),
            "delete",
            id,
        )
        return ApiController.delete(self, ver, register, subregister, id, id2)

    def search(self, ver=None, register=None):
        id = None
        try:
            params = MultiDict(self._get_search_params(request.params))
            if "q" in list(params.keys()):
                id = params["q"]
            if "query" in list(params.keys()):
                id = params["query"]
        except ValueError as e:
            log.debug(str(e))
            pass
        self._post_analytics(c.user, register, "search", id)

        return ApiController.search(self, ver, register)
