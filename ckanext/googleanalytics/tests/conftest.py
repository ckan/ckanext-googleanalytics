import factory
import pytest
from factory.alchemy import SQLAlchemyModelFactory
from pytest_factoryboy import register

import ckan.model as model

from ckanext.googleanalytics.model import PackageStats, ResourceStats


@pytest.fixture()
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("googleanalytics")


@register
class PackageStatsFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = model.Session
        model = PackageStats

    package_id = factory.Faker("uuid4")
    visits_recently = factory.Faker("pyint")
    visits_ever = factory.Faker("pyint")


@register
class ResourceStatsFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = model.Session
        model = ResourceStats

    resource_id = factory.Faker("uuid4")
    visits_recently = factory.Faker("pyint")
    visits_ever = factory.Faker("pyint")
