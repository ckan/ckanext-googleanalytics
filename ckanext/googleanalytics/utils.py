import ast
import json
import logging

import requests
from six.moves.urllib.parse import urlencode
import ckantoolkit as tk

log = logging.getLogger(__name__)

DEFAULT_RESOURCE_URL_TAG = "/downloads/"
DEFAULT_RECENT_VIEW_DAYS = 14
EVENT_API = "CKAN API Request"


def config_id():
    return tk.config["googleanalytics.id"]


def config_tracking_mode():
    type_ = tk.config.get("googleanalytics.tracking_mode")
    if type_:
        return type_

    id_ = config_id()

    if id_.startswith("UA-"):
        return "ga"

    if id_.startswith("G-"):
        return "gtag"

    return "ga"


def config_measurement_protocol_client_id():
    return tk.config.get("googleanalytics.measurement_protocol.client_id")


def config_measurement_protocol_client_secret():
    return tk.config.get("googleanalytics.measurement_protocol.client_secret")


def config_measurement_protocol_api_whitelist():
    return tk.aslist(
        tk.config.get("googleanalytics.measurement_protocol.api_tracking_whitelist")
    )


def config_account():
    return tk.config.get("googleanalytics.account")


def config_profile_id():
    return tk.config.get("googleanalytics.profile_id")


def config_credentials():
    return tk.config.get("googleanalytics.credentials.path")


def config_domain():
    return tk.config.get("googleanalytics.domain", "auto")


def config_fields():
    fields = ast.literal_eval(tk.config.get("googleanalytics.fields", "{}"))

    if config_linked_domains():
        fields["allowLinker"] = "true"

    return fields


def config_linked_domains():
    googleanalytics_linked_domains = tk.config.get(
        "googleanalytics.linked_domains", ""
    )
    return [x.strip() for x in googleanalytics_linked_domains.split(",") if x]


def config_enable_user_id():
    return tk.asbool(tk.config.get("googleanalytics.enable_user_id", False))


def config_prefix():
    return tk.config.get(
        "googleanalytics_resource_prefix", DEFAULT_RESOURCE_URL_TAG
    )


def config_recent_view_days():
    return tk.asint(
        tk.config.get(
            "googleanalytics.recent_view_days", DEFAULT_RECENT_VIEW_DAYS
        )
    )


def send_event(data):
    if isinstance(data, MeasurementProtocolData):
        if data["event"] != EVENT_API:
            log.warning("Only API event supported by Measurement Protocol at the moment")
            return

        return _mp_api_handler({
            "action": data["object"],
            "payload": data["payload"],
        })


    return _ga_handler(data)


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, _):
        return None


def _mp_api_handler(data_dict):
    whitelist = set(config_measurement_protocol_api_whitelist())
    if whitelist and data_dict["action"] not in whitelist:
        log.debug(
            "Skip sending %s API action to Google Analytics because it is not whitelisted",
            data_dict["action"]
        )
        return

    log.debug(
        "Sending API event to Google Analytics using the Measurement Protocol: %s",
        data_dict
    )
    resp = requests.post(
        "https://www.google-analytics.com/mp/collect",
        params={
            "api_secret": config_measurement_protocol_client_secret(),
            "measurement_id": config_id()
        },
        data=json.dumps({
            "client_id": config_measurement_protocol_client_id(),
            "non_personalized_ads": False,
            "events":[{
                "name": data_dict["action"],
                "params": data_dict["payload"]
            }]
        }, cls=SafeJSONEncoder)
    )
    # breakpoint()
    if resp.status_code >= 300:
        log.error("Cannot post event: %s", resp)


def _ga_handler(data_dict):
    data = urlencode(data_dict)
    log.debug("Sending API event to Google Analytics: %s", data)

    requests.post(
        "http://www.google-analytics.com/collect",
        data,
        timeout=10,
    )


class UniversalAnalyticsData(dict):
    pass


class MeasurementProtocolData(dict):
    pass
