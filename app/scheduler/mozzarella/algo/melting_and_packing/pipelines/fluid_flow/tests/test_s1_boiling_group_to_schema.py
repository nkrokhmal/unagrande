import os

from app.scheduler.mozzarella.algo.melting_and_packing import BoilingGroupToSchema
from app.scheduler.mozzarella.boiling_plan import read_boiling_plan
from utils_ak.pandas import mark_consecutive_groups

os.environ["APP_ENVIRONMENT"] = "interactive"
from app.imports.runtime import *

warnings.filterwarnings("ignore")


def test(use_interactive_environment):
    df = read_boiling_plan(
        config.abs_path(
            "app/data/static/samples/inputs/mozzarella/2021-02-09 План по варкам.xlsx"
        )
    )
    mark_consecutive_groups(df, "boiling", "boiling_group")
    boiling_group_df = df[df["boiling_group"] == 2]
    boiling_volumes, boilings_meltings, packings = BoilingGroupToSchema()(
        boiling_group_df
    )
    print(boiling_volumes, boilings_meltings, packings)


if __name__ == "__main__":
    test(True)
