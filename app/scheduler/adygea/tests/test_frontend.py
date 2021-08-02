from app.imports.runtime import *
from app.scheduler.adygea import *


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(wrap_boiling(make_boiling(boiling_model)))


def _test(fn, open_file=False):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_adygea(fn, open_file=open_file)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs(reset=True)


def test_batch():
    fns = glob.glob(
        config.abs_path("app/data/static/samples/inputs/by_department/ricotta/*.xlsx")
    )
    fns = [fn for fn in fns if "$" not in fn]
    for fn in tqdm.tqdm(fns):
        _test(fn, open_file=False)


if __name__ == "__main__":
    _test(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_department/adygea/План по варкам адыгейский 1.xlsx",
        open_file=True,
    )
    # test_batch()
