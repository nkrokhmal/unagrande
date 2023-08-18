def saturate_boiling_plan(boiling_plan_df):
    df = boiling_plan_df.copy()
    df["boiling"] = df["sku"].apply(lambda sku: delistify(sku.made_from_boilings, single=True))
    df["start"] = None
    df["finish"] = None
    return df
