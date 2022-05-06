import pytest

from ckan.tests.helpers import call_action
import ckan.plugins.toolkit as tk
import ckan.model as model


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestPackageStatsShow:

    def test_existing(self, package_stats):
        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "googleanalytics_package_stats_show",
                id=package_stats.package_id
            )
        model.Session.commit()

        rec = call_action(
            "googleanalytics_package_stats_show", id=package_stats.package_id
        )

        assert rec["visits_recently"] == rec["visits_recently"]
        assert rec["visits_ever"] == rec["visits_ever"]


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestResourceStatsShow:

    def test_existing(self, resource_stats):
        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "googleanalytics_resource_stats_show",
                id=resource_stats.resource_id
            )
        model.Session.commit()

        rec = call_action(
            "googleanalytics_resource_stats_show",
            id=resource_stats.resource_id
        )

        assert rec["visits_recently"] == rec["visits_recently"]
        assert rec["visits_ever"] == rec["visits_ever"]
