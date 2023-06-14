import pytest

import ckan.plugins.toolkit as tk
from ckanext.googleanalytics import config


@pytest.mark.usefixtures("with_plugins", "with_request_context")
class TestCodeSnippets:
    @pytest.mark.parametrize("mode", ["ga", "gtag", "gtm"])
    @pytest.mark.parametrize("tracking_id", ["UA-123", "G-123", "GTM-123"])
    def test_tracking_(self, mode, tracking_id, app, ckan_config, monkeypatch):
        snippet = tk.h.googleanalytics_header()
        monkeypatch.setitem(ckan_config, config.CONFIG_TRACKING_ID, tracking_id)
        monkeypatch.setitem(ckan_config, config.CONFIG_TRACKING_MODE, mode)
        snippet = tk.render_snippet("googleanalytics/snippets/_{}.html".format(mode), {
            "googleanalytics_id": tracking_id,
            "googleanalytics_domain": config.domain(),
            "googleanalytics_fields": config.fields(),
            "googleanalytics_linked_domains": config.linked_domains()
        })
        resp = app.get("/")
        assert snippet in resp.body
