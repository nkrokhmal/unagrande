"""empty message

Revision ID: 337a649c60f0
Revises: 
Create Date: 2021-03-30 14:14:03.890801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "337a649c60f0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("short_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mozzarella_cooling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_cooling_time", sa.Integer(), nullable=True),
        sa.Column("second_cooling_time", sa.Integer(), nullable=True),
        sa.Column("salting_time", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pack_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "packers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "batch_number",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("datetime", sa.Date(), nullable=True),
        sa.Column("beg_number", sa.Integer(), nullable=True),
        sa.Column("end_number", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cream_cheese_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cooling_time", sa.Integer(), nullable=True),
        sa.Column("separation_time", sa.Integer(), nullable=True),
        sa.Column("salting_time", sa.Integer(), nullable=True),
        sa.Column("p_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mozzarella_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pouring_time", sa.Integer(), nullable=True),
        sa.Column("soldification_time", sa.Integer(), nullable=True),
        sa.Column("cutting_time", sa.Integer(), nullable=True),
        sa.Column("pouring_off_time", sa.Integer(), nullable=True),
        sa.Column("pumping_out_time", sa.Integer(), nullable=True),
        sa.Column("extra_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("heating_time", sa.Integer(), nullable=True),
        sa.Column("delay_time", sa.Integer(), nullable=True),
        sa.Column("protein_harvest_time", sa.Integer(), nullable=True),
        sa.Column("abandon_time", sa.Integer(), nullable=True),
        sa.Column("pumping_out_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "washer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("time", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.Column("boiling_technology_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["boiling_technology_id"],
            ["boiling_technologies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cream_cheese_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("params", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "form_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("relative_weight", sa.Integer(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mascarpone_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("params", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mozzarella_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("input_ton", sa.Integer(), nullable=True),
        sa.Column("output_ton", sa.Integer(), nullable=True),
        sa.Column("pouring_time", sa.Integer(), nullable=True),
        sa.Column("serving_time", sa.Integer(), nullable=True),
        sa.Column("melting_speed", sa.Integer(), nullable=True),
        sa.Column("chedderization_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("input_ton", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "steam_consumption",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("params", sa.String(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "FormFactorMadeFromMadeTo",
        sa.Column("ParentChildId", sa.Integer(), nullable=False),
        sa.Column("ParentId", sa.Integer(), nullable=True),
        sa.Column("ChildId", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["ChildId"],
            ["form_factors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["ParentId"],
            ["form_factors.id"],
        ),
        sa.PrimaryKeyConstraint("ParentChildId"),
    )
    op.create_table(
        "cream_cheese_boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("percent", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cream_cheese_form_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["form_factors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mascarpone_boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("flavoring_agent", sa.String(), nullable=True),
        sa.Column("percent", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mascarpone_fermentator",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("output_ton", sa.Integer(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["mascarpone_lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mascarpone_fermentators",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("output_ton", sa.Integer(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["mascarpone_lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mascarpone_form_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["form_factors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mozzarella_boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("percent", sa.Float(), nullable=True),
        sa.Column("is_lactose", sa.Boolean(), nullable=True),
        sa.Column("ferment", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mozzarella_form_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("default_cooling_technology_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["default_cooling_technology_id"],
            ["mozzarella_cooling_technologies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id"],
            ["form_factors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("flavoring_agent", sa.String(), nullable=True),
        sa.Column("percent", sa.Integer(), nullable=True),
        sa.Column("number_of_tanks", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_form_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["form_factors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("brand_name", sa.String(), nullable=True),
        sa.Column("weight_netto", sa.Float(), nullable=True),
        sa.Column("shelf_life", sa.Integer(), nullable=True),
        sa.Column("collecting_speed", sa.Integer(), nullable=True),
        sa.Column("packing_speed", sa.Integer(), nullable=True),
        sa.Column("in_box", sa.Integer(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.Column("form_factor_id", sa.Integer(), nullable=True),
        sa.Column("pack_type_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["form_factor_id"],
            ["form_factors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["lines.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pack_type_id"],
            ["pack_types.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cream_cheese_skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mascarpone_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pouring_time", sa.Integer(), nullable=True),
        sa.Column("heating_time", sa.Integer(), nullable=True),
        sa.Column("adding_lactic_acid_time", sa.Integer(), nullable=True),
        sa.Column("separation_time", sa.Integer(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.Column("fermentator_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fermentator_id"],
            ["mascarpone_fermentators.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["mascarpone_lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mascarpone_skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mozzarella_skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("production_by_request", sa.Boolean(), nullable=True),
        sa.Column("packing_by_request", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_analyses_technology",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("preparation_time", sa.Integer(), nullable=True),
        sa.Column("analysis_time", sa.Integer(), nullable=True),
        sa.Column("pumping_time", sa.Integer(), nullable=True),
        sa.Column("boiling_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["boiling_id"],
            ["ricotta_boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("output_per_tank", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sku_boiling",
        sa.Column("boiling_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["boiling_id"],
            ["boilings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sku_id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("boiling_id", "sku_id"),
    )
    op.create_table(
        "sku_packer",
        sa.Column("packer_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["packer_id"],
            ["packers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sku_id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("packer_id", "sku_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sku_packer")
    op.drop_table("sku_boiling")
    op.drop_table("ricotta_skus")
    op.drop_table("ricotta_analyses_technology")
    op.drop_table("mozzarella_skus")
    op.drop_table("mascarpone_skus")
    op.drop_table("mascarpone_boiling_technologies")
    op.drop_table("cream_cheese_skus")
    op.drop_table("skus")
    op.drop_table("ricotta_form_factors")
    op.drop_table("ricotta_boilings")
    op.drop_table("mozzarella_form_factors")
    op.drop_table("mozzarella_boilings")
    op.drop_table("mascarpone_form_factors")
    op.drop_table("mascarpone_fermentators")
    op.drop_table("mascarpone_fermentator")
    op.drop_table("mascarpone_boilings")
    op.drop_table("cream_cheese_form_factors")
    op.drop_table("cream_cheese_boilings")
    op.drop_table("FormFactorMadeFromMadeTo")
    op.drop_table("steam_consumption")
    op.drop_table("ricotta_lines")
    op.drop_table("mozzarella_lines")
    op.drop_table("mascarpone_lines")
    op.drop_table("form_factors")
    op.drop_table("cream_cheese_lines")
    op.drop_table("boilings")
    op.drop_table("washer")
    op.drop_table("ricotta_boiling_technologies")
    op.drop_table("mozzarella_boiling_technologies")
    op.drop_table("lines")
    op.drop_table("cream_cheese_boiling_technologies")
    op.drop_table("batch_number")
    op.drop_table("packers")
    op.drop_table("pack_types")
    op.drop_table("mozzarella_cooling_technologies")
    op.drop_table("groups")
    op.drop_table("departments")
    op.drop_table("boiling_technologies")
    # ### end Alembic commands ###
