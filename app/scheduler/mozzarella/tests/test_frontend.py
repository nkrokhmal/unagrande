from app.imports.runtime import *
from app.enum import LineName
from app.scheduler.mozzarella import run_mozzarella


def test_batch():
    fns = glob.glob(
        config.abs_path(
            "app/data/static/samples/inputs/by_department/mozzarella/*.xlsx"
        )
    )
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(utils.tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix="new " + str(i))


def _test(fn, *args, **kwargs):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_mozzarella(fn, *args, **kwargs)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    utils.configure_loguru()
    _test(
        config.abs_path(
            "/Users/marklidenberg/Desktop/2021-09-11 Расписание моцарелла (2).xlsx"
        ),
        start_times={LineName.WATER: "07:35", LineName.SALT: "05:25"},
        first_boiling_id=1,
        open_file=True,
        prefix="new3",
    )
    # test_batch()
