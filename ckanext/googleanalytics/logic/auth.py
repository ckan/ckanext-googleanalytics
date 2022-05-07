from __future__ import absolute_import

from ckan.authz import is_authorized


def get_auth():
    return dict(
        googleanalytics_package_stats_show=package_stats_show,
        googleanalytics_resource_stats_show=resource_stats_show,
    )


def package_stats_show(context, data_dict):
    return is_authorized("package_show", context, data_dict)


def resource_stats_show(context, data_dict):
    return is_authorized("resource_show", context, data_dict)
