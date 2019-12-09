# -*- coding: utf-8 -*-

import hashlib
import logging

from flask import Blueprint

import ckan.logic as logic
import ckan.plugins.toolkit as tk
import ckan.views.api as api
import ckan.views.resource as resource

from ckan.common import g

log = logging.getLogger(__name__)
ga = Blueprint("google_analytics", "google_analytics")


def action(logic_function, ver=api.API_MAX_VERSION):
    try:
        function = logic.get_action(logic_function)
        side_effect_free = getattr(function, "side_effect_free", False)
        request_data = api._get_request_data(try_url_params=side_effect_free)
        if isinstance(request_data, dict):
            id = request_data.get("id", "")
            if "q" in request_data:
                id = request_data["q"]
            if "query" in request_data:
                id = request_data[u"query"]
            _post_analytics(g.user, "CKAN API Request", logic_function, "", id)
    except Exception as e:
        log.debug(e)
        pass

    return api.action(logic_function, ver)


ga.add_url_rule(
    "/api/action/<logic_function>", methods=["GET", "POST"], view_func=action,
)
ga.add_url_rule(
    u"/<int(min=3, max={0}):ver>/action/<logic_function>".format(
        api.API_MAX_VERSION
    ),
    methods=["GET", "POST"],
    view_func=action,
)


def download(id, resource_id, filename=None, package_type="dataset"):
    _post_analytics(
        g.user,
        "CKAN Resource Download Request",
        "Resource",
        "Download",
        resource_id,
    )
    return resource.download(package_type, id, resource_id, filename)


ga.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/download", view_func=download
)
ga.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/download/<filename>",
    view_func=download,
)


def _post_analytics(
    user, event_type, request_obj_type, request_function, request_id
):

    from ckanext.googleanalytics.plugin import GoogleAnalyticsPlugin

    if tk.config.get("googleanalytics.id"):
        data_dict = {
            "v": 1,
            "tid": tk.config.get("googleanalytics.id"),
            "cid": hashlib.md5(tk.c.user).hexdigest(),
            # customer id should be obfuscated
            "t": "event",
            "dh": tk.request.environ["HTTP_HOST"],
            "dp": tk.request.environ["PATH_INFO"],
            "dr": tk.request.environ.get("HTTP_REFERER", ""),
            "ec": event_type,
            "ea": request_obj_type + request_function,
            "el": request_id,
        }
        GoogleAnalyticsPlugin.analytics_queue.put(data_dict)
