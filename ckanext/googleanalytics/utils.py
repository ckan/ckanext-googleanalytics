import ast

import ckantoolkit as tk

DEFAULT_RESOURCE_URL_TAG = "/downloads/"
DEFAULT_RECENT_VIEW_DAYS = 14


def config_id():
    return tk.config["googleanalytics.id"]


def config_account():
    return tk.config.get("googleanalytics.account")


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
