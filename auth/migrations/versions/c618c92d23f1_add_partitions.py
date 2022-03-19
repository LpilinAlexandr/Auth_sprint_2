"""empty message

Revision ID: c618c92d23f1
Revises: 
Create Date: 2022-03-19 17:36:51.099956

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c618c92d23f1'
down_revision = '2cc417f6c642'
branch_labels = None
depends_on = None


def downgrade():
    op.drop_table('login_history_p2')
    op.drop_table('login_history_p7')
    op.drop_table('login_history_p12')
    op.drop_table('login_history_p16')
    op.drop_table('login_history_p20')
    op.drop_table('login_history_p6')
    op.drop_table('login_history_p11')
    op.drop_table('login_history_p17')
    op.drop_table('login_history_p4')
    op.drop_table('login_history_p15')
    op.drop_table('login_history_p8')
    op.drop_table('login_history_p14')
    op.drop_table('login_history_p10')
    op.drop_table('login_history_p19')
    op.drop_table('login_history_p13')
    op.drop_table('login_history_p1')
    op.drop_table('login_history_p18')
    op.drop_table('login_history_p3')
    op.drop_table('login_history_p5')
    op.drop_table('login_history_p9')


def upgrade():
    for number in range(5):
        n = 4 * number
        year = 2 + number
        next_year = 3 + number
        op.execute(
            f"""CREATE TABLE IF NOT EXISTS "login_history_p{1 + n}"
                PARTITION OF "login_history"
                FOR VALUES FROM ('202{year}-01-01') TO ('202{year}-04-01');
                CREATE INDEX ON "login_history_p{1 + n}" (created_at);
            """
        )
        op.execute(
            f"""CREATE TABLE IF NOT EXISTS "login_history_p{2 + n}"
                PARTITION OF "login_history"
                FOR VALUES FROM ('202{year}-04-01') TO ('202{year}-07-01');
                CREATE INDEX ON "login_history_p{2 + n}" (created_at);
            """
        )
        op.execute(
            f"""CREATE TABLE IF NOT EXISTS "login_history_p{3 + n}"
                PARTITION OF "login_history"
                FOR VALUES FROM ('202{year}-07-01') TO ('202{year}-10-01');
                CREATE INDEX ON "login_history_p{3 + n}" (created_at);
            """
        )
        op.execute(
            f"""CREATE TABLE IF NOT EXISTS "login_history_p{4 + n}"
                PARTITION OF "login_history"
                FOR VALUES FROM ('202{year}-10-01') TO ('202{next_year}-01-01');
                CREATE INDEX ON "login_history_p{4 + n}" (created_at);
            """
        )
