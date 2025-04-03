from __future__ import absolute_import
import itertools as it
import operator as op
import ckan.plugins.toolkit as tk
from ckan.logic import validate
from google.analytics.data import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    MetricHeader,
    DimensionHeader,
)

from . import schema
from .. import config
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

    client = BetaAnalyticsDataClient.from_service_account_file(config.credentials())

    params = {
        "property": f"properties/{config.property_id()}",
        "dimensions": [{"name": d} for d in data_dict.get("dimensions", [])],
        "metrics": [{"name": m} for m in data_dict.get("metrics", ["eventCount"])],
        "date_ranges": [
            {
                "start_date": data_dict["start_date"].date().isoformat(),
                "end_date": data_dict["end_date"].date().isoformat(),
            }
        ],
    }

    if "name" in data_dict:
        params["dimension_filter"] = {
            "filter": {
                "field_name": "eventName",
                "string_filter": {"value": data_dict["name"]},
            }
        }

    request = RunReportRequest(**params)

    response = client.run_report(request)

    header_names = it.chain(response.dimension_headers, response.metric_headers)

    return {
        "headers": [h.name for h in header_names],
        "rows": [
            [v.value for v in row.dimension_values]
            + [v.value for v in row.metric_values]
            for row in response.rows
        ],
    }
