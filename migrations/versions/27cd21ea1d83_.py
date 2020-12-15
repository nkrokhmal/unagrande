"""empty message

Revision ID: 27cd21ea1d83
Revises: 
Create Date: 2020-12-07 18:33:18.302669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27cd21ea1d83'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('boilings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('percent', sa.Float(), nullable=True),
    sa.Column('is_lactose', sa.Boolean(), nullable=True),
    sa.Column('ferment', sa.String(), nullable=True),
    sa.Column('pouring_id', sa.Integer(), nullable=True),
    sa.Column('melting_id', sa.Integer(), nullable=True),
    sa.Column('line_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['line_id'], ['lines.id'], ),
    sa.ForeignKeyConstraint(['melting_id'], ['meltings.id'], ),
    sa.ForeignKeyConstraint(['pouring_id'], ['pourings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cheesemakers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cheese_maker_name', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('possible_volumes', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('form_factors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('short_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('global_pouring_processes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pouring_time', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Integer(), nullable=True),
    sa.Column('cheddarization_time', sa.Integer(), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('meltings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serving_time', sa.Integer(), nullable=True),
    sa.Column('melting_time', sa.Integer(), nullable=True),
    sa.Column('speed', sa.Integer(), nullable=True),
    sa.Column('first_cooling_time', sa.Integer(), nullable=True),
    sa.Column('second_cooling_time', sa.Integer(), nullable=True),
    sa.Column('salting_time', sa.Integer(), nullable=True),
    sa.Column('boiling_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['boiling_id'], ['boilings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pack_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('packers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pourings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pouring_time', sa.Integer(), nullable=True),
    sa.Column('soldification_time', sa.Integer(), nullable=True),
    sa.Column('cutting_time', sa.Integer(), nullable=True),
    sa.Column('pouring_off_time', sa.Integer(), nullable=True),
    sa.Column('extra_time', sa.Integer(), nullable=True),
    sa.Column('boiling_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['boiling_id'], ['boilings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('priorities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('form_factor_id', sa.Integer(), nullable=True),
    sa.Column('boiling_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['boiling_id'], ['boilings.id'], ),
    sa.ForeignKeyConstraint(['form_factor_id'], ['form_factors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sku_boiling',
    sa.Column('boiling_id', sa.Integer(), nullable=False),
    sa.Column('sku_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['boiling_id'], ['boilings.id'], ),
    sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ),
    sa.PrimaryKeyConstraint('boiling_id', 'sku_id')
    )
    op.create_table('skus',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('brand_name', sa.String(), nullable=True),
    sa.Column('weight_netto', sa.Float(), nullable=True),
    sa.Column('weight_form_factor', sa.Float(), nullable=True),
    sa.Column('output_per_ton', sa.Integer(), nullable=True),
    sa.Column('shelf_life', sa.Integer(), nullable=True),
    sa.Column('packing_speed', sa.Integer(), nullable=True),
    sa.Column('packing_reconfiguration', sa.Integer(), nullable=True),
    sa.Column('is_rubber', sa.Boolean(), nullable=True),
    sa.Column('packing_reconfiguration_format', sa.Integer(), nullable=True),
    sa.Column('packer_id', sa.Integer(), nullable=True),
    sa.Column('pack_type_id', sa.Integer(), nullable=True),
    sa.Column('form_factor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['form_factor_id'], ['form_factors.id'], ),
    sa.ForeignKeyConstraint(['pack_type_id'], ['pack_types.id'], ),
    sa.ForeignKeyConstraint(['packer_id'], ['packers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('termizators',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('short_cleaning_time', sa.Integer(), nullable=True),
    sa.Column('long_cleaning_time', sa.Integer(), nullable=True),
    sa.Column('pouring_time', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('termizators')
    op.drop_table('skus')
    op.drop_table('sku_boiling')
    op.drop_table('priorities')
    op.drop_table('pourings')
    op.drop_table('packers')
    op.drop_table('pack_types')
    op.drop_table('meltings')
    op.drop_table('lines')
    op.drop_table('global_pouring_processes')
    op.drop_table('form_factors')
    op.drop_table('departments')
    op.drop_table('cheesemakers')
    op.drop_table('boilings')
    # ### end Alembic commands ###