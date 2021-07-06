from app.utils.features.draw_utils import *
from app.utils.features.openpyxl_wrapper import ExcelBlock
from app.models import MascarponeSKU
from app.utils.files.utils import create_dir


def update_total_schedule_task(date, df):
    data_dir = create_dir(
        date.strftime(flask.current_app.config["DATE_FORMAT"]),
        "task"
    )
    path = os.path.join(data_dir, f"{date.date()}.csv")
    columns = ["sku", "code", "in_box", "kg", "boxes_count"]
    if not os.path.exists(path):
        df_task = pd.DataFrame(columns=columns)
        df_task.to_csv(path, index=False, sep=";")

    df_task = pd.read_csv(path, sep=";")
    df["sku_name"] = df["sku"].apply(lambda x: x.name)

    sku_names = db.session.query(MascarponeSKU).all()
    sku_names = [x.name for x in sku_names]
    df_task = df_task[~df_task['sku'].isin(sku_names)]

    for sku_name, grp in df.groupby("sku_name"):
        kg = round(grp["kg"].sum())
        boxes_count = math.ceil(
            grp["kg"].sum()
            / grp.iloc[0]["sku"].in_box
            / grp.iloc[0]["sku"].weight_netto
        )
        values = [
            sku_name,
            grp.iloc[0]["sku"].code,
            grp.iloc[0]["sku"].in_box,
            kg,
            boxes_count,
        ]
        df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)
    df_task.to_csv(path, index=False, sep=";")


def draw_task_original(excel_client, df, date, cur_row, task_name):
    df_filter = df
    index = 1

    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name)

    for sku_name, grp in df_filter.groupby("sku_name"):
        kg = round(grp["kg"].sum())
        boxes_count = math.ceil(
            grp["kg"].sum()
            / grp.iloc[0]["sku"].in_box
            / grp.iloc[0]["sku"].weight_netto
        )
        values = [
            index,
            sku_name,
            grp.iloc[0]["sku"].in_box,
            kg,
            boxes_count,
            grp.iloc[0]["sku"].code,
        ]
        excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
        index += 1
    return cur_row


def draw_task_new(excel_client, df, date, cur_row, task_name, batch_number):
    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name, "варки")
    for boiling_group_id, grp in df.groupby("boiling_id"):
        for i, row in grp.iterrows():
            if row["sku"].in_box:
                kg = round(row["kg"])
                boxes_count = math.ceil(
                    row["kg"] / row["sku"].in_box / row["sku"].weight_netto
                )
            else:
                kg = round(row["kg"])
                boxes_count = ""

            values = [
                boiling_group_id + batch_number - 1,
                row["sku_name"],
                row["sku"].in_box,
                kg,
                boxes_count,
                row["sku"].code,
            ]
            excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
        excel_client = draw_blue_line(excel_client, cur_row)
        cur_row += 1
    return cur_row


def schedule_task_boilings(wb, df, date, batch_number):
    df_copy = df.copy()
    df_copy["sku_name"] = df_copy["sku"].apply(lambda sku: sku.name)
    sheet_name = "Печать заданий"
    mascarpone_task_name = "Задание на упаковку Маскарпонного цеха"

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name], font_size=9)

    cur_row = draw_task_original(
        excel_client,
        df_copy,
        date,
        cur_row,
        mascarpone_task_name,
    )
    cur_row += space_row
    return wb
