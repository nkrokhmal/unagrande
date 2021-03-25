import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.ricotta.boiling_plan import *
from config import DebugConfig


def test_read_boiling_plan():
    print(
        read_boiling_plan(
            DebugConfig.abs_path("app/data/inputs/ricotta/sample_boiling_plan.xlsx")
        )
    )


if __name__ == "__main__":
    test_read_boiling_plan()
