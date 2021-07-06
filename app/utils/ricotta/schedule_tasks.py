from app.utils.features.draw_utils import *
from app.utils.features.openpyxl_wrapper import ExcelBlock
from app.models import RicottaSKU
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

    sku_names = db.session.query(RicottaSKU).all()
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


def schedule_task_boilings(wb, df, date, batch_number):
    df_copy = df.copy()
    df_copy["sku_name"] = df_copy["sku"].apply(lambda sku: sku.name)
    sheet_name = "Печать заданий"
    ricotta_task_name = "Задание на упаковку Рикоттного цеха"

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name], font_size=9)

    cur_row = draw_task_original(
        excel_client,
        df_copy,
        date,
        cur_row,
        ricotta_task_name,
    )
    cur_row += space_row
    return wb
