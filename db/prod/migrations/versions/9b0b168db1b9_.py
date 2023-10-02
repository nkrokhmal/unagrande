"""empty message

Revision ID: 9b0b168db1b9
Revises: 
Create Date: 2023-10-02 20:27:37.400267

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "9b0b168db1b9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "batch_number",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("datetime", sa.Date(), nullable=True),
        sa.Column("beg_number", sa.Integer(), nullable=True),
        sa.Column("end_number", sa.Integer(), nullable=True),
        sa.Column("group", sa.String(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
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
        "washer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_name", sa.String(), nullable=True),
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
        "adygea_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lunch_time", sa.Integer(), nullable=True),
        sa.Column("preparation_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("output_coeff", sa.Float(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["line_id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "butter_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("preparing_time", sa.Integer(), nullable=True),
        sa.Column("displacement_time", sa.Integer(), nullable=True),
        sa.Column("output_kg", sa.Integer(), nullable=True),
        sa.Column("cleaning_time", sa.Integer(), nullable=True),
        sa.Column("boiling_volume", sa.Integer(), nullable=True),
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
        sa.Column("cream_reconfiguration_short", sa.Integer(), nullable=True),
        sa.Column("cream_reconfiguration_long", sa.Integer(), nullable=True),
        sa.Column("creamcheese_reconfiguration", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["lines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "milk_project_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("water_collecting_time", sa.Integer(), nullable=True),
        sa.Column("equipment_check_time", sa.Integer(), nullable=True),
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
        sa.Column("output_kg", sa.Integer(), nullable=True),
        sa.Column("pouring_time", sa.Integer(), nullable=True),
        sa.Column("serving_time", sa.Integer(), nullable=True),
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
        sa.Column("input_kg", sa.Integer(), nullable=True),
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
        "adygea_boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("weight_netto", sa.Float(), nullable=True),
        sa.Column("input_kg", sa.Integer(), nullable=True),
        sa.Column("output_kg", sa.Integer(), nullable=True),
        sa.Column("percent", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "adygea_form_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["form_factors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("boiling_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["boiling_id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "butter_boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("weight_netto", sa.Float(), nullable=True),
        sa.Column("flavoring_agent", sa.String(), nullable=True),
        sa.Column("is_lactose", sa.Boolean(), nullable=True),
        sa.Column("percent", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "butter_form_factors",
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
        sa.Column("boiling_type", sa.String(), nullable=True),
        sa.Column("weight_netto", sa.Float(), nullable=True),
        sa.Column("is_lactose", sa.Boolean(), nullable=True),
        sa.Column("flavoring_agent", sa.String(), nullable=True),
        sa.Column("percent", sa.Float(), nullable=True),
        sa.Column("input_kg", sa.Float(), nullable=True),
        sa.Column("output_constant", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
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
        "milk_project_boilings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("weight_netto", sa.Float(), nullable=True),
        sa.Column("output_kg", sa.Integer(), nullable=True),
        sa.Column("percent", sa.Integer(), nullable=True),
        sa.Column("equipment_check_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boilings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "milk_project_form_factors",
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
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("flavoring_agent", sa.String(), nullable=True),
        sa.Column("percent", sa.Integer(), nullable=True),
        sa.Column("input_kg", sa.Integer(), nullable=True),
        sa.Column("output_kg", sa.Integer(), nullable=True),
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
        sa.Column("code", sa.String(), nullable=True),
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
        "adygea_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collecting_time", sa.Integer(), nullable=True),
        sa.Column("coagulation_time", sa.Integer(), nullable=True),
        sa.Column("pouring_off_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "adygea_skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "butter_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("separator_runaway_time", sa.Integer(), nullable=True),
        sa.Column("pasteurization_time", sa.Integer(), nullable=True),
        sa.Column("increasing_temperature_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "butter_skus",
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
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.Column("separation_time", sa.Integer(), nullable=True),
        sa.Column("analysis_time", sa.Integer(), nullable=True),
        sa.Column("pouring_time", sa.Integer(), nullable=True),
        sa.Column("heating_time", sa.Integer(), nullable=True),
        sa.Column("pumping_time", sa.Integer(), nullable=True),
        sa.Column("salting_time", sa.Integer(), nullable=True),
        sa.Column("ingredient_time", sa.Integer(), nullable=True),
        sa.Column("line_id", sa.Integer(), nullable=True),
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
        "milk_project_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mixture_collecting_time", sa.Integer(), nullable=True),
        sa.Column("processing_time", sa.Integer(), nullable=True),
        sa.Column("red_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "milk_project_skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["skus.id"],
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
        "mozzarella_skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("melting_speed", sa.Integer(), nullable=True),
        sa.Column("production_by_request", sa.Boolean(), nullable=True),
        sa.Column("packing_by_request", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["skus.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_boiling_technologies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pouring_time", sa.Integer(), nullable=True),
        sa.Column("heating_time", sa.Integer(), nullable=True),
        sa.Column("lactic_acid_time", sa.Integer(), nullable=True),
        sa.Column("drain_whey_time", sa.Integer(), nullable=True),
        sa.Column("dray_ricotta_time", sa.Integer(), nullable=True),
        sa.Column("salting_time", sa.Integer(), nullable=True),
        sa.Column("pumping_time", sa.Integer(), nullable=True),
        sa.Column("ingredient_time", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["boiling_technologies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ricotta_skus",
        sa.Column("id", sa.Integer(), nullable=False),
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
    op.drop_table("ricotta_boiling_technologies")
    op.drop_table("mozzarella_skus")
    op.drop_table("mozzarella_boiling_technologies")
    op.drop_table("milk_project_skus")
    op.drop_table("milk_project_boiling_technologies")
    op.drop_table("mascarpone_skus")
    op.drop_table("mascarpone_boiling_technologies")
    op.drop_table("butter_skus")
    op.drop_table("butter_boiling_technologies")
    op.drop_table("adygea_skus")
    op.drop_table("adygea_boiling_technologies")
    op.drop_table("skus")
    op.drop_table("ricotta_form_factors")
    op.drop_table("ricotta_boilings")
    op.drop_table("mozzarella_form_factors")
    op.drop_table("mozzarella_boilings")
    op.drop_table("milk_project_form_factors")
    op.drop_table("milk_project_boilings")
    op.drop_table("mascarpone_form_factors")
    op.drop_table("mascarpone_boilings")
    op.drop_table("butter_form_factors")
    op.drop_table("butter_boilings")
    op.drop_table("boiling_technologies")
    op.drop_table("adygea_form_factors")
    op.drop_table("adygea_boilings")
    op.drop_table("FormFactorMadeFromMadeTo")
    op.drop_table("steam_consumption")
    op.drop_table("ricotta_lines")
    op.drop_table("mozzarella_lines")
    op.drop_table("milk_project_lines")
    op.drop_table("mascarpone_lines")
    op.drop_table("form_factors")
    op.drop_table("butter_lines")
    op.drop_table("boilings")
    op.drop_table("adygea_lines")
    op.drop_table("washer")
    op.drop_table("lines")
    op.drop_table("batch_number")
    op.drop_table("users")
    op.drop_table("packers")
    op.drop_table("pack_types")
    op.drop_table("mozzarella_cooling_technologies")
    op.drop_table("groups")
    op.drop_table("departments")
    # ### end Alembic commands ###
