import pytest

from ckanext.googleanalytics import config


@pytest.mark.parametrize(("tracking_id", "mode"), [
    ("UA-123", "ga"),
    ("G-123", "gtag"),
    ("GTM-123", "gtm"),
    ("HELLO-123", "ga"),
])
def test_tracking_mode(tracking_id, mode, monkeypatch, ckan_config):
    monkeypatch.setitem(ckan_config, config.CONFIG_TRACKING_ID, tracking_id)
    assert mode == config.tracking_mode()
