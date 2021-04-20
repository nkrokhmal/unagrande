import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.ricotta.algo.schedule import *
from app.schedule_maker.departments.ricotta.boiling_plan import *
from config import DebugConfig


def test_random():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = generate_random_boiling_plan()
    print(make_schedule(boiling_plan_df))


def test_sample():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path("app/data/inputs/ricotta/sample_boiling_plan.xlsx")
    )
    print(make_schedule(boiling_plan_df))


if __name__ == "__main__":
    test_sample()