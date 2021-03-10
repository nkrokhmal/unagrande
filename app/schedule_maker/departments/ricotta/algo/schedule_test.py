import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.ricotta.algo.schedule import *
from app.schedule_maker.departments.ricotta.boiling_plan import (
    generate_random_boiling_plan,
)


def test():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = generate_random_boiling_plan()
    print(make_schedule(boiling_plan_df))


if __name__ == "__main__":
    test()
