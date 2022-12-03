import json
import logging

import requests
from six.moves.urllib.parse import urlencode
from ckan.plugins import PluginImplementations
from ckanext.googleanalytics import config, interfaces


log = logging.getLogger(__name__)

EVENT_API = "CKAN API Request"


def send_event(data):
    for p in PluginImplementations(interfaces.IGoogleAnalytics):
        if p.googleanalytics_skip_event(data):
            return

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

    log.debug(
        "Sending API event to Google Analytics using the Measurement Protocol: %s",
        data_dict
    )
    resp = requests.post(
        "https://www.google-analytics.com/mp/collect",
        params={
            "api_secret": config.measurement_protocol_client_secret(),
            "measurement_id": config.measurement_id()
        },
        data=json.dumps({
            "client_id": config.measurement_protocol_client_id(),
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
