from app.imports.runtime import *
from app.scheduler import draw_excel_frontend
from app.scheduler.contour_cleanings.algo.schedule import *
from app.scheduler.contour_cleanings.frontend import *
from app.scheduler.contour_cleanings import run_contour_cleanings


def test(open_file=False):
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()

    outputs = run_contour_cleanings(
        "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/sample1",
        prefix="sample1",
        open_file=open_file,
        butter_end_time="16:00",
        adygea_end_time="20:00",
    )
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs(reset=True)


if __name__ == "__main__":
    test(open_file=True)
