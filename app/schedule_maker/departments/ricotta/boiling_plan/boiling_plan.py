from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.enum import LineName


def read_boiling_plan(wb_obj):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = cast_workbook(wb_obj)

    ws_name = "План варок"
    ws = wb[ws_name]
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
            "Номер варки",
            "SKU",
            "КГ",
        ]
    ]
    df.columns = [
        "boiling_id",
        "sku",
        "kg",
    ]

    # remove separators and empty lines
    df = df[df["sku"] != "-"]
    df = df[~df["kg"].isnull()]

    df["sku"] = df["sku"].apply(lambda sku: cast_model(RicottaSKU, sku))

    df["boiling"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0])
    print(df["boiling_id"])
    df["boiling_id"] = df["boiling_id"].astype(int)
    # for idx, grp in df.groupby("boiling_id"):
        # assert (
        #     len(grp["boiling"].unique()) == 1
        # ), "В одной группе варок должен быть только один тип варки."

    # todo: make properly
    # # validate kilograms
    # for idx, grp in df.groupby("boiling_id"):
    #     boiling = grp.iloc[0]["boiling"]
    #     if (
    #         abs(grp["kg"].sum() - boiling.output)
    #         / grp.iloc[0]["total_volume"]
    #         > 0.05
    #     ):
    #         raise AssertionError(
    #             "Одна из групп варок имеет неверное количество килограмм."
    #         )
    #     else:
    #         if abs(grp["kg"].sum() - grp.iloc[0]["total_volume"]) > 1e-5:
    #             # todo: warning message
    #             df.loc[grp.index, "kg"] *= (
    #                 grp.iloc[0]["total_volume"] / grp["kg"].sum()
    #             )  # scale to total_volume
    #         else:
    #             # all fine
    #             pass
    return df