from app.scheduler.contour_cleanings.algo.schedule import make_schedule
from app.scheduler.contour_cleanings.frontend.frontend import wrap_frontend
from app.scheduler.contour_cleanings.frontend.style import STYLE
from app.scheduler.load_properties import load_properties
from app.scheduler.load_schedules import load_schedules
from app.scheduler.submit_schedule import submit_schedule


def run_contour_cleanings(
    input_path,
    output_path="outputs/",
    schedule=None,
    schedules=None,
    properties=None,
    prefix="",
    open_file=False,
    **kwargs,
):
    if not schedule:
        if not properties:
            if not schedules:
                schedules = load_schedules(input_path, prefix=prefix)

            # todo maybe: need a check here?
            # assert_schedules_presence(
            #     schedules,
            #     raise_if_not_present=["ricotta"],
            #     warn_if_not_present=[
            #         "mozzarella",
            #         "butter",
            #         "adygea",
            #         "milk_project",
            #         "mascarpone",
            #     ],
            # )

            properties = load_properties(schedules, path=input_path, prefix=prefix)

        schedule = make_schedule(properties, **kwargs)
    frontend = wrap_frontend(schedule)
    return submit_schedule(
        "контурные мойки",
        schedule,
        frontend,
        prefix,
        STYLE,
        path=output_path,
        open_file=open_file,
    )
