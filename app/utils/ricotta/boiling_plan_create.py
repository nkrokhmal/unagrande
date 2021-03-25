import pandas as pd
from app.utils.features.merge_boiling_utils import Boilings
from collections import namedtuple


def boiling_plan_create(df):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["flavoring_agent"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].flavoring_agent
    )
    df["number_of_tanks"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].number_of_tanks
    )
    df["short_display_name"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].short_display_name
    )
    df["group"] = df["sku"].apply(lambda x: x.group.name)
    df["is_cream"] = df["sku"].apply(lambda x: x.made_from_boilings[0].is_cream)
    df["output_per_tank"] = df["sku"].apply(lambda x: x.output_per_tank)

    result, boiling_number = handle_ricotta(df)
    result["kg"] = result["plan"]
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result["output"] = result["output_per_tank"] * result["number_of_tanks"]
    result["boiling_type"] = result["sku"].apply(
        lambda sku: sku.made_from_boilings[0].to_str()
    )
    result = result[
        ["id", "number_of_tanks", "group", "output", "name", "boiling_type", "kg"]
    ]
    return result


def handle_ricotta(df):
    boilings_ricotta = Boilings()
    Order = namedtuple("Collection", "is_cream, flavoring_agent")
    orders = [
        Order(True, None),
        Order(False, ""),
        Order(False, "Ваниль"),
        Order(False, "Шоколад"),
        Order(False, "Шоколад-орех"),
    ]
    for order in orders:
        df_filter = df[
            (df["is_cream"] == order.is_cream)
            & (
                order.flavoring_agent is None
                or df["flavoring_agent"] == order.flavoring_agent
            )
        ]
        if not df_filter.empty:
            df_filter['output'] = df_filter["number_of_tanks"] * df_filter["output_per_tank"]
            df_filter['output'] = df_filter['output'].apply(lambda x: int(x))
            df_filter_groups = [group for _, group in df_filter.groupby('output')]
            for df_filter_group in df_filter_groups:
                max_weight = df_filter_group['output'].iloc[0]
                print(max_weight)
                boilings_ricotta.add_group(
                    df_filter_group.to_dict("records"), max_weight=max_weight
                )
    boilings_ricotta.finish()
    return pd.DataFrame(boilings_ricotta.boilings), boilings_ricotta.boiling_number
