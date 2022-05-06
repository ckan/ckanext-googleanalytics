from __future__ import absolute_import

import ckan.plugins.toolkit as tk
from ckan.logic import validate

from . import schema
from ..model import PackageStats, ResourceStats


def get_actions():
    return dict(
        googleanalytics_package_stats_show=googleanalytics_package_stats_show,
        googleanalytics_resource_stats_show=googleanalytics_resource_stats_show
    )


@validate(schema.googleanalytics_package_stats_show)
@tk.side_effect_free
def googleanalytics_package_stats_show(context, data_dict):
    tk.check_access("googleanalytics_package_stats_show", context, data_dict)
    rec = (
        context["session"]
        .query(PackageStats)
        .filter(PackageStats.package_id == data_dict["id"])
        .one_or_none()
    )

    if not rec:
        raise tk.ObjectNotFound()

    return rec.for_json(context)


@validate(schema.googleanalytics_resource_stats_show)
@tk.side_effect_free
def googleanalytics_resource_stats_show(context, data_dict):
    tk.check_access("googleanalytics_resource_stats_show", context, data_dict)
    rec = (
        context["session"]
        .query(ResourceStats)
        .filter(ResourceStats.resource_id == data_dict["id"])
        .one_or_none()
    )

    if not rec:
        raise tk.ObjectNotFound()

    return rec.for_json(context)
