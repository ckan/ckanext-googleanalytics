"""empty message

Revision ID: b74febeb899b
Revises:
Create Date: 2022-05-06 17:46:09.398679

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "b74febeb899b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if "package_stats" not in tables:
        _create_package_stats()

    if "resource_stats" not in tables:
        _create_resource_stats()


def downgrade():
    op.drop_table("resource_stats")
    op.drop_table("package_stats")


def _create_package_stats():
    op.create_table(
        "package_stats",
        sa.Column("package_id", sa.String(60), primary_key=True),
        sa.Column("visits_recently", sa.Integer),
        sa.Column("visits_ever", sa.Integer),
    )


def _create_resource_stats():
    op.create_table(
        "resource_stats",
        sa.Column("resource_id", sa.String(60), primary_key=True),
        sa.Column("visits_recently", sa.Integer),
        sa.Column("visits_ever", sa.Integer),
    )
