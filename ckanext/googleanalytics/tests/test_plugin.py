import pytest


@pytest.mark.usefixtures("clean_db")
def test_script(app):
    resp = app.get("/")
    assert "GoogleAnalyticsObject" in resp
