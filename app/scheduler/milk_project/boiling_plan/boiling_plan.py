from app.enum import LineName
from app.imports.runtime import *
from app.models import *
from app.scheduler.boiling_plan import *

from .saturate import saturate_boiling_plan


def read_boiling_plan(wb_obj, first_batch_ids=None):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    first_batch_ids = first_batch_ids or {"milk_project": 1}
    wb = utils.cast_workbook(wb_obj)

    cur_id = 0

    with code("Load boiling plan"):
        ws = None
        for key in ["План варок", "План варок милкпроджект"]:
            if key in wb.sheetnames:
                ws = wb[key]
        if not ws:
            raise Exception("Не найдена вкладка для плана варок")

    values = []

    # collect header
    header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

    for i in range(2, 200):
        if not ws.cell(i, 2).value:
            continue

        values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])

    df = pd.DataFrame(values, columns=header)
    df = df[
        [
            "Номер группы варок",
            "SKU",
            "КГ",
        ]
    ]
    df.columns = [
        "group_id",
        "sku",
        "kg",
    ]
    df = df[df["sku"] != "-"]
    df["group_id"] = df["group_id"].astype(int)

    # batch_id and boiling_id are the same with group_id
    df["batch_id"] = df["group_id"]
    df["boiling_id"] = df["group_id"]

    df["sku"] = df["sku"].apply(lambda sku: cast_model(MilkProjectSKU, sku))

    df = saturate_boiling_plan(df)
    df["batch_type"] = "milk_project"
    df = update_absolute_batch_id(df, first_batch_ids)
    return df
