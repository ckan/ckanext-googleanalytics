# -*- coding: utf-8 -*-
import Queue as queue

import hashlib
import importlib

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckanext.googleanalytics import config

from ckan.controllers.package import PackageController
from routes.mapper import SubMapper


class GAMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes)

    analytics_queue = queue.Queue()

    def before_map(self, map):
        """Add new routes that this extension's controllers handle.

        See IRoutes.

        """
        # Helpers to reduce code clutter
        GET = dict(method=["GET"])
        PUT = dict(method=["PUT"])
        POST = dict(method=["POST"])
        DELETE = dict(method=["DELETE"])
        GET_POST = dict(method=["GET", "POST"])
        # intercept API calls that we want to capture analytics on
        register_list = [
            "package",
            "dataset",
            "resource",
            "tag",
            "group",
            "related",
            "revision",
            "licenses",
            "rating",
            "user",
            "activity",
        ]
        register_list_str = "|".join(register_list)
        # /api ver 3 or none
        with SubMapper(
            map,
            controller="ckanext.googleanalytics.controller:GAApiController",
            path_prefix="/api{ver:/3|}",
            ver="/3",
        ) as m:
            m.connect(
                "/action/{logic_function}",
                action="action",
                conditions=GET_POST,
            )

        # /api ver 1, 2, 3 or none
        with SubMapper(
            map,
            controller="ckanext.googleanalytics.controller:GAApiController",
            path_prefix="/api{ver:/1|/2|/3|}",
            ver="/1",
        ) as m:
            m.connect("/search/{register}", action="search")

        # /api/rest ver 1, 2 or none
        with SubMapper(
            map,
            controller="ckanext.googleanalytics.controller:GAApiController",
            path_prefix="/api{ver:/1|/2|}",
            ver="/1",
            requirements=dict(register=register_list_str),
        ) as m:

            m.connect("/rest/{register}", action="list", conditions=GET)
            m.connect("/rest/{register}", action="create", conditions=POST)
            m.connect("/rest/{register}/{id}", action="show", conditions=GET)
            m.connect("/rest/{register}/{id}", action="update", conditions=PUT)
            m.connect(
                "/rest/{register}/{id}", action="update", conditions=POST
            )
            m.connect(
                "/rest/{register}/{id}", action="delete", conditions=DELETE
            )

        return map

    def after_map(self, map):
        """Add new routes that this extension's controllers handle.

        See IRoutes.

        """
        self._modify_resource_download_route(map)
        map.redirect("/analytics/package/top", "/analytics/dataset/top")
        map.connect(
            "analytics",
            "/analytics/dataset/top",
            controller="ckanext.googleanalytics.controller:GAController",
            action="view",
        )
        return map

    def _modify_resource_download_route(self, map):
        """Modifies resource_download method in related controller
        to attach GA tracking code.
        """

        if "_routenames" in map.__dict__:
            if "resource_download" in map.__dict__["_routenames"]:
                route_data = map.__dict__["_routenames"][
                    "resource_download"
                ].__dict__
                route_controller = route_data["defaults"]["controller"].split(
                    ":"
                )
                module = importlib.import_module(route_controller[0])
                controller_class = getattr(module, route_controller[1])
                controller_class.resource_download = wrap_resource_download(
                    controller_class.resource_download
                )
            else:
                # If no custom uploader applied, use the default one
                PackageController.resource_download = wrap_resource_download(
                    PackageController.resource_download
                )


def wrap_resource_download(func):
    def func_wrapper(cls, id, resource_id, filename=None):
        _post_analytics(
            tk.c.user,
            "CKAN Resource Download Request",
            "Resource",
            "Download",
            resource_id,
        )

        return func(cls, id, resource_id, filename=None)

    return func_wrapper


def _post_analytics(
    user, event_type, request_obj_type, request_function, request_id
):
    data_dict = {
        "v": 1,
        "tid": config.tracking_id(),
        "cid": hashlib.md5(tk.c.user).hexdigest(),
        # customer id should be obfuscated
        "t": "event",
        "dh": tk.c.environ["HTTP_HOST"],
        "dp": tk.c.environ["PATH_INFO"],
        "dr": tk.c.environ.get("HTTP_REFERER", ""),
        "ec": event_type,
        "ea": request_obj_type + request_function,
        "el": request_id,
    }
    GAMixinPlugin.analytics_queue.put(data_dict)
