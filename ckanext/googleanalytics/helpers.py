
import ast

import ckan.plugins.toolkit as tk


def get_helpers():
    return {
        "googleanalytics_header": header,
    }

def header():
    """Render the googleanalytics_header snippet for CKAN 2.0 templates.

    This is a template helper function that renders the
    googleanalytics_header jinja snippet. To be called from the jinja
    templates in this extension, see ITemplateHelpers.

    """

    fields = _fields()

    if _enable_user_id() and tk.c.user:
        fields["userId"] = str(tk.c.userobj.id)

    data = {
        "googleanalytics_id": _id(),
        "googleanalytics_domain": _domain(),
        "googleanalytics_fields": str(fields),
        "googleanalytics_linked_domains": _linked_domains(),
    }
    return tk.render_snippet(
        "googleanalytics/snippets/googleanalytics_header.html", data
    )


def _id():
    return tk.config["googleanalytics.id"]

def _domain():
    return tk.config.get(
        "googleanalytics.domain", "auto"
    )

def _fields():
    fields = ast.literal_eval(
            tk.config.get("googleanalytics.fields", "{}")
        )

    if _linked_domains():
        fields["allowLinker"] = "true"

    return fields

def _linked_domains():
    googleanalytics_linked_domains = tk.config.get(
            "googleanalytics.linked_domains", ""
        )
    return [
            x.strip() for x in googleanalytics_linked_domains.split(",") if x
    ]


def _enable_user_id():
    return tk.asbool(
        tk.config.get("googleanalytics.enable_user_id", False)
    )
