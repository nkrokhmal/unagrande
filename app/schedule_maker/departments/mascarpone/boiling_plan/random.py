import random
from app.schedule_maker.models import *


def generate_random_boiling_plan(n=3, seed=12):
    random.seed(seed)

    mascarpone_ids = range(82, 91)  # todo: take from table properly
    mascarpone_model_ids = range(16, 20)  # todo: take from table properly
    sku_ids = mascarpone_ids
    boiling_model_ids = mascarpone_model_ids

    skus = [cast_model(MascarponeSKU, sku_id) for sku_id in sku_ids]
    skus

    values = []
    for i in range(n):
        boiling_model = cast_model(MascarponeBoiling, random.choice(boiling_model_ids))

        for j in range(2):
            sku = random.choice(
                [sku for sku in skus if boiling_model in sku.made_from_boilings]
            )

            values.append([i * 2 + j, sku, 10])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    return df