import ast
import logging

from werkzeug.utils import import_string

import ckan.plugins.toolkit as tk

CONFIG_TRACKING_ID = "googleanalytics.id"
CONFIG_PROPERTY_ID = "googleanalytics.property_id"
CONFIG_HANDLER_PATH = "googleanalytics.download_handler"
CONFIG_TRACKING_MODE = "googleanalytics.tracking_mode"

DEFAULT_RESOURCE_URL_TAG = "/downloads/"
DEFAULT_RECENT_VIEW_DAYS = 14


log = logging.getLogger(__name__)


def tracking_id():
    # type: () -> str
    return tk.config["googleanalytics.id"]


def property_id():
    # type: () -> str
    return tk.config[CONFIG_PROPERTY_ID]


def download_handler():
    handler_path = tk.config.get(CONFIG_HANDLER_PATH)
    if handler_path:
        handler = import_string(handler_path, silent=True)
    else:
        handler = None
        log.warning(("Missing {} config option.").format(CONFIG_HANDLER_PATH))

    return handler


def tracking_mode():
    # type: () -> Literal["ga", "gtag", "gtm"]
    type_ = tk.config.get(CONFIG_TRACKING_MODE)
    if type_:
        return type_

    id_ = tracking_id()

    if id_.startswith("UA-"):
        return "ga"

    if id_.startswith("G-"):
        return "gtag"

    if id_.startswith("GTM-"):
        return "gtm"

    return "ga"


def measurement_id():
    # type: () -> str
    """Set the MeasurementID for tracking API actions. By default,
    `googleanalytics.id` is used.

    Use this option during migration from Universal Analytics, to track API
    requests using Measurement Protocol, while tracking browser event using
    Universal Analytics.

    Requires `googleanalytics.measurement_protocol.client_id`.
    """
    return tk.config.get("googleanalytics.measurement_protocol.id") or tracking_id()


def measurement_protocol_client_id():
    # type: () -> str | None
    return tk.config.get("googleanalytics.measurement_protocol.client_id")


def measurement_protocol_client_secret():
    return tk.config.get("googleanalytics.measurement_protocol.client_secret")


def measurement_protocol_track_downloads():
    # type: () -> bool
    return tk.asbool(
        tk.config.get("googleanalytics.measurement_protocol.track_downloads")
    )


def account():
    return tk.config.get("googleanalytics.account")


def profile_id():
    return tk.config.get("googleanalytics.profile_id")


def credentials():
    return tk.config.get("googleanalytics.credentials.path")


def domain():
    return tk.config.get("googleanalytics.domain", "auto")


def fields():
    fields = ast.literal_eval(tk.config.get("googleanalytics.fields", "{}"))

    if linked_domains():
        fields["allowLinker"] = "true"

    return fields


def linked_domains():
    googleanalytics_linked_domains = tk.config.get(
        "googleanalytics.linked_domains", ""
    )
    return [x.strip() for x in googleanalytics_linked_domains.split(",") if x]


def enable_user_id():
    return tk.asbool(tk.config.get("googleanalytics.enable_user_id", False))


def prefix():
    return tk.config.get(
        "googleanalytics_resource_prefix", DEFAULT_RESOURCE_URL_TAG
    )


def recent_view_days():
    return tk.asint(
        tk.config.get(
            "googleanalytics.recent_view_days", DEFAULT_RECENT_VIEW_DAYS
        )
    )
