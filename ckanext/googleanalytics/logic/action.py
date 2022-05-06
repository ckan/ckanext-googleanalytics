from __future__ import absolute_import

import ckan.plugins.toolkit as tk
from ckan.logic import validate

from . import schema
from .. import utils
from ..model import PackageStats, ResourceStats
from ..ga_auth import init_service, get_profile_id


def get_actions():
    return dict(
        googleanalytics_package_stats_show=package_stats_show,
        googleanalytics_resource_stats_show=resource_stats_show,
        googleanalytics_event_report=event_report,
    )


@validate(schema.package_stats_show)
@tk.side_effect_free
def package_stats_show(context, data_dict):
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


@validate(schema.resource_stats_show)
@tk.side_effect_free
def resource_stats_show(context, data_dict):
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


@validate(schema.event_report)
@tk.side_effect_free
def event_report(context, data_dict):
    tk.check_access("sysadmin", context, data_dict)

    se = init_service(utils.config_credentials())
    filters = "ga:eventAction=={action};ga:eventCategory=={category}".format(
        action=data_dict["action"], category=data_dict["category"]
    )
    if "label" in data_dict:
        filters += ";ga:eventLabel=={label}".format(label=data_dict["label"])

    report = (
        se.data()
        .ga()
        .get(
            ids="ga:{id}".format(id=get_profile_id(se)),
            dimensions=",".join(data_dict["dimensions"]),
            metrics=",".join(data_dict["metrics"]),
            start_date=data_dict["start_date"].date().isoformat(),
            end_date=data_dict["end_date"].date().isoformat(),
            filters=filters,
        )
        .execute()
    )

    return {
        "headers": [h["name"] for h in report["columnHeaders"]],
        "rows": report["rows"],
    }
