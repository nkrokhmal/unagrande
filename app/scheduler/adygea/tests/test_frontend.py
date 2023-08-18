import glob
import os
import warnings

import tqdm

from utils_ak.lazy_tester.lazy_tester_class import lazy_tester

from config import config


def _test(fn, open_file=False, *args, **kwargs):
    lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_adygea(
        fn, open_file=open_file, start_time="07:00", prepare_start_time="07:00", first_batch_id=11, *args, **kwargs
    )
    lazy_tester.log(outputs["schedule"])
    lazy_tester.assert_logs(reset=False)


def test_batch():
    fns = glob.glob(config.abs_path("app/data/static/samples/inputs/by_department/adygea/*.xlsx"))
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix=str(i))


if __name__ == "__main__":
    _test(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_department/adygea/План по варкам адыгейский 1.xlsx",
        open_file=False,
    )
    # test_batch()
