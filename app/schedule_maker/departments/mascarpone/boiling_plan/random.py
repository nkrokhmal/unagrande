import random
from app.schedule_maker.models import *


def _generate_random_boiling_group(sku_model, boiling_model, n=3, seed=12):
    random.seed(seed)

    skus = fetch_all(sku_model)
    models = fetch_all(boiling_model)

    values = []
    for i in range(n):
        boiling_model = random.choice(models)

        for j in range(2):
            sku = random.choice(
                [sku for sku in skus if boiling_model in sku.made_from_boilings]
            )
            kg = sku.packing_speed * np.random.uniform(0.6, 0.8) / 2
            kg = custom_round(kg, 10, "ceil")
            values.append([i * 2 + j, sku, kg])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    return df


def generate_random_boiling_plan(n_groups=4, seed=17):
    dfs = []
    for i in range(n_groups):
        group_type = random.choice(["Mascarpone", "CreamCheese"])
        sku_model = globals()[group_type + "SKU"]
        boiling_model = globals()[group_type + "Boiling"]
        df = _generate_random_boiling_group(sku_model, boiling_model, seed=seed + i)
        dfs.append(df)

    res = pd.concat(dfs, axis=0)

    res["boiling_id"] = range(len(res))
    res["boiling_id"] //= 2
    return res
