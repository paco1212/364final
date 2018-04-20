"""adding ranking

Revision ID: 12f083fecced
Revises: 2628718fc98f
Create Date: 2018-04-20 16:22:03.302016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12f083fecced'
down_revision = '2628718fc98f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strains', sa.Column('ranking', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('strains', 'ranking')
    # ### end Alembic commands ###