import os

from utils_ak.openpyxl.openpyxl_tools import cast_workbook, draw_sheet_sequence
from utils_ak.os.os_tools import makedirs, open_file_in_os

from app.scheduler.frontend_utils import prepare_schedule_worksheet
from config import config


def run_consolidated(
    input_path,
    prefix="",
    departments=None,
    add_contour_cleanings=True,
    output_path="outputs/",
    wb=None,
    open_file=False,
):
    departments = departments or [
        "mozzarella",
        "ricotta",
        "milk_project",
        "butter",
        "mascarpone",
    ]
    makedirs(output_path)

    fns = [
        os.path.join(
            input_path,
            f"{prefix} Расписание {config.DEPARTMENT_ROOT_NAMES[department]}.xlsx",
        )
        for department in departments
    ]
    if add_contour_cleanings:
        fns.append(
            os.path.join(
                input_path,
                f"{prefix} Расписание контурные мойки.xlsx",
            )
        )

    fns = [fn for fn in fns if os.path.exists(fn)]
    wb = wb or ["Расписание"]
    wb = cast_workbook(wb)
    prepare_schedule_worksheet((wb, "Расписание"))
    draw_sheet_sequence((wb, "Расписание"), [(fn, "Расписание") for fn in fns])
    output_fn = os.path.join(output_path, prefix + " Расписание общее.xlsx")
    wb.save(output_fn)
    if open_file:
        open_file_in_os(output_fn)
    return wb


def test():
    run_consolidated(
        # "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/",
        "/Users/arsenijkadaner/Desktop/2022-01-21/approved",
        add_contour_cleanings=True,
        prefix="2022-01-21",
        open_file=True,
    )


if __name__ == "__main__":
    test()