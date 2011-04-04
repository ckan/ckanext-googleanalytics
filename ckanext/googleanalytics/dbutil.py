import ckan.model as model
from ckan.authz import Authorizer
from ckan.model.authz import PSEUDO_USER__VISITOR
from ckan.lib.base import *


def init_tables():
    try:
        connection = model.Session.connection()
        connection.execute("""CREATE TABLE package_stats (
        package_id varchar(60) primary key,
        visits_recently integer,
        visits_ever integer);""")
    except Exception, e:
        if not "already exists" in e.args[0]:
            raise
    model.Session.commit()
    try:
        connection = model.Session.connection()
        connection.execute("""CREATE TABLE resource_stats (
        resource_id varchar(60) primary key,
        visits_recently integer,
        visits_ever integer);""")
    except Exception, e:
        if not "already exists" in e.args[0]:
            raise
    model.Session.commit()


def update_resource_visits(resource_id, recently, ever):
    connection = model.Session.connection()
    count = connection.execute(
        """SELECT count(resource_id) FROM resource_stats
        WHERE resource_id = '%s'""" % resource_id).fetchone()
    if count[0]:
        connection.execute(
            """UPDATE resource_stats SET visits_recently = %s,
            visits_ever = %s
            WHERE resource_id = '%s'""" % (recently, ever, resource_id)
            )
    else:
        connection.execute(
            """INSERT INTO resource_stats
            (resource_id, visits_recently, visits_ever) VALUES
            ('%s', %s, %s)""" % (resource_id, recently, ever))


def get_resource_visits_for_url(url):
    connection = model.Session.connection()
    count = connection.execute(
        """SELECT visits_ever FROM resource_stats, resource
        WHERE resource_id = resource.id
        AND resource.url = '%s'""" % url).fetchone()
    return count and count[0] or ""


def update_package_visits(package_id, recently, ever):
    connection = model.Session.connection()
    count = connection.execute(
        """SELECT count(package_id) FROM package_stats
        WHERE package_id = '%s'""" % package_id).fetchone()
    if count[0]:
        connection.execute(
            """UPDATE package_stats SET visits = %s
            WHERE package_id = '%s'""" % (recently, ever, package_id)
            )
    else:
        connection.execute(
            """INSERT INTO package_stats
            (package_id, visits_recently, visits_ever) VALUES
            ('%s', %s, %s)""" % (package_id, recently, ever))


def get_top_packages(limit=20):
    items = []
    authorizer = Authorizer()
    q = authorizer.authorized_query(PSEUDO_USER__VISITOR,
                                    model.Package)
    connection = model.Session.connection()
    res = connection.execute("""SELECT package_id, visits_recently
    FROM package_stats
    ORDER BY visits_recently DESC;""").fetchmany(limit)
    for package_id, visits in res:
        item = q.filter("package.id = '%s'" % package_id)
        if not item.count():
            continue
        items.append((item.first(), visits))
    return items
