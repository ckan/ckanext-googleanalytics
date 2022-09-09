
import ckan.plugins.toolkit as tk
from ckanext.googleanalytics import config


def get_helpers():
    return {
        "googleanalytics_header": googleanalytics_header,
        "googleanalytics_resource_prefix": googleanalytics_resource_prefix,
        "googleanalytics_tracking_mode": googleanalytics_tracking_mode,
    }


def googleanalytics_resource_prefix():

    return config.prefix()


def googleanalytics_header():
    """Render the googleanalytics_header snippet for CKAN 2.0 templates.

    This is a template helper function that renders the
    googleanalytics_header jinja snippet. To be called from the jinja
    templates in this extension, see ITemplateHelpers.

    """

    fields = config.fields()

    if config.enable_user_id() and tk.c.user:
        fields["userId"] = str(tk.c.userobj.id)

    data = {
        "googleanalytics_id": config.tracking_id(),
        "googleanalytics_domain": config.domain(),
        "googleanalytics_fields": str(fields),
        "googleanalytics_linked_domains": config.linked_domains(),
    }
    return tk.render_snippet(
        "googleanalytics/snippets/googleanalytics_header.html", data
    )


def googleanalytics_tracking_mode():
    return config.tracking_mode()
