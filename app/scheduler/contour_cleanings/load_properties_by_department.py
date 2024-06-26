import os

import flask

from loguru import logger

from app.scheduler.adygea.properties.adygea_properties import cast_properties as cast_properties_adygea
from app.scheduler.adygea.properties.parse_properties import parse_properties as parse_properties_adygea
from app.scheduler.archive.mascarpone.properties import cast_properties as cast_properties_mascarpone
from app.scheduler.archive.ricotta.properties import cast_properties as cast_properties_ricotta
from app.scheduler.butter.properties.butter_properties import cast_properties as cast_properties_butter
from app.scheduler.butter.properties.parse_properties import parse_properties as parse_properties_butter
from app.scheduler.milk_project.properties.milk_project_properties import (
    cast_properties as cast_properties_milk_project,
)
from app.scheduler.milk_project.properties.parse_properties import parse_properties as parse_properties_milk_project

# from app.scheduler.mozzarella.properties.mozzarella_properties import cast_properties as cast_properties_mozzarella
from app.scheduler.mozzarella.properties.parse_properties import parse_properties as parse_properties_mozzarella
from config import config


SCHEDULE_PARSERS = {
    # "mozzarella": cast_properties_mozzarella,
    "milk_project": cast_properties_milk_project,
    "butter": cast_properties_butter,
    "adygea": cast_properties_adygea,
    "ricotta": cast_properties_ricotta,
    "mascarpone": cast_properties_mascarpone,
}

EXCEL_PARSERS = {
    "mozzarella": parse_properties_mozzarella,
    "milk_project": parse_properties_milk_project,
    "butter": parse_properties_butter,
    "adygea": parse_properties_adygea,
}


def load_properties_by_department(
    schedules_by_department,
    path=None,
    prefix=None,
):
    # NOTE: RETURN BLANK PROPERTIES IF NOT PRESENT
    properties = {}

    for department in [
        "mozzarella",
        "milk_project",
        "butter",
        "adygea",
        "ricotta",
        "mascarpone",
    ]:
        if department in schedules_by_department.keys():
            properties[department] = SCHEDULE_PARSERS[department](schedules_by_department[department])
        else:
            # try to find in files

            if path and prefix:
                filename = os.path.join(
                    path,
                    f"{prefix} Расписание {config.DEPARTMENT_ROOT_NAMES_BY_DEPARTMENT[department]}.xlsx",
                )
                if os.path.exists(filename):
                    try:
                        properties[department] = EXCEL_PARSERS[department](filename)
                    except:
                        # raise
                        raise Exception(
                            f"Произошла ошибка во время чтения параметров расписания из файла: {os.path.basename(filename)}"
                        )
                else:
                    # init empty properties
                    properties[department] = SCHEDULE_PARSERS[department]()
            else:
                # init empty properties
                properties[department] = SCHEDULE_PARSERS[department]()
    return properties


def assert_properties_presence(properties, raise_if_not_present=None, warn_if_not_present=None):
    raise_if_not_present = raise_if_not_present or []
    warn_if_not_present = warn_if_not_present or []

    for department in raise_if_not_present:
        if not properties[department].is_present():
            raise Exception(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES_BY_DEPARTMENT[department]}"
            )

    for department in warn_if_not_present:
        if not properties[department].is_present():
            logger.warning(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES_BY_DEPARTMENT[department]}"
            )
            if os.environ.get("APP_ENVIRONMENT") == "runtime":
                flask.flash(
                    f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES_BY_DEPARTMENT[department]}",
                    "warning",
                )


def test():
    print(
        load_properties_by_department(
            schedules_by_department={},
            path="/Users/marklidenberg/Downloads/Telegram Desktop/",
            prefix="2021-09-03",
        )
    )


if __name__ == "__main__":
    test()
