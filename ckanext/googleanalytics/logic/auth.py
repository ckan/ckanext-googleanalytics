from __future__ import absolute_import

from ckan.authz import is_authorized


def get_auth():
    return dict(
        googleanalytics_package_stats_show=googleanalytics_package_stats_show,
        googleanalytics_resource_stats_show=googleanalytics_resource_stats_show
    )


def googleanalytics_package_stats_show(context, data_dict):
    return {"success": is_authorized("package_show", context, data_dict)}


def googleanalytics_resource_stats_show(context, data_dict):
    return {"success": is_authorized("resource_show", context, data_dict)}
