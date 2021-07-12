from app.imports.runtime import *
from app.scheduler import *


def test_day(
    input_path, prefix, output_path="outputs/", input_params=None, open_file=False
):
    input_params = input_params or {}

    run_mozzarella(
        os.path.join(input_path, prefix + " " + "План по варкам моцарелла.xlsx"),
        prefix=prefix,
        **input_params.get("mozzarella", {})
    )
    run_ricotta(
        os.path.join(input_path, prefix + " " + "План по варкам рикотта.xlsx"),
        prefix=prefix,
        **input_params.get("ricotta", {})
    )
    run_mascarpone(
        os.path.join(input_path, prefix + " " + "План по варкам маскарпоне.xlsx"),
        prefix=prefix,
        **input_params.get("mascarpone", {})
    )
    run_butter(
        os.path.join(input_path, prefix + " " + "План по варкам масло.xlsx"),
        prefix=prefix,
        **input_params.get("butter", {})
    )
    run_milk_project(
        os.path.join(input_path, prefix + " " + "План по варкам милкпроджект.xlsx"),
        prefix=prefix,
        **input_params.get("milk_project", {})
    )
    run_contour_cleanings(
        output_path, prefix=prefix, **input_params.get("contour_cleanings", {})
    )
    run_consolidated(
        output_path,
        prefix=prefix,
        open_file=open_file,
    )


if __name__ == "__main__":
    test_day(
        input_path="/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/sample1",
        output_path="/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/sample1",
        prefix="sample1",
        open_file=False,
    )
