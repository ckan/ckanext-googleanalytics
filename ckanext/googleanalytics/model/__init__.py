from __future__ import absolute_import

from sqlalchemy import Column, String, Integer

from ckan.lib.dictization import table_dictize

from .base import Base


class PackageStats(Base):
    __tablename__ = "package_stats"

    package_id = Column(String(60), primary_key=True)
    visits_recently = Column(Integer)
    visits_ever = Column(Integer)

    def for_json(self, context):
        return table_dictize(self, context)


class ResourceStats(Base):
    __tablename__ = "resource_stats"

    resource_id = Column(String(60), primary_key=True)
    visits_recently = Column(Integer)
    visits_ever = Column(Integer)

    def for_json(self, context):
        return table_dictize(self, context)
