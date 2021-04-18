from utils_ak.block_tree import *
from utils_ak.iteration import *
from utils_ak.builtin import *

from app.schedule_maker.models import *


def make_boiling(boiling_model):
    maker, make = init_block_maker(
        "boiling", boiling_model=boiling_model
    )  # copy boiling_model for working tests
    bt = delistify(boiling_model.boiling_technologies, single=True)
    make("heating", size=(bt.heating_time // 5, 0))
    make("delay", size=(bt.delay_time // 5, 0))
    make("protein_harvest", size=(bt.protein_harvest_time // 5, 0))
    make("abandon", size=(bt.abandon_time // 5, 0))

    if not boiling_model.flavoring_agent:
        make("pumping_out", size=(bt.pumping_out_time // 5, 0))
    else:
        # make pumping_out parallel with abandon
        make(
            "pumping_out",
            size=(bt.pumping_out_time // 5, 0),
            x=(maker.root["abandon"].y[0] - bt.pumping_out_time // 5, 0),
            push_func=add_push,
        )

    steam_value = (
        900 if not boiling_model.flavoring_agent else 673
    )  # todo: take from parameters
    make(
        "steam_consumption",
        size=(maker.root["heating"].size[0], 0),
        x=(0, 0),
        value=steam_value,
        push_func=add_push,
    )
    return maker.root


def make_boiling_sequence(boiling_group_df):
    maker, make = init_block_maker("boiling_sequence")

    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]
    n_tanks = boiling_group_df.iloc[0]["tanks"]

    boilings = [make_boiling(boiling_model) for _ in range(n_tanks)]

    for b_prev, b in SimpleIterator(boilings).iter_sequences(2, method="any"):
        if not b:
            continue

        if not b_prev:
            push(maker.root, b, push_func=add_push)
        else:
            b.props.update(x=(b_prev["delay"].x[0], 0))
            push(maker.root, b, push_func=add_push)
    return maker.root


def make_boiling_group(boiling_group_df):
    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]
    n_tanks = boiling_group_df.iloc[0]["tanks"]
    group_tanks = boiling_group_df.iloc[0]["group_tanks"]
    first_tank = boiling_group_df.iloc[0]["first_tank"]
    maker, make = init_block_maker(
        "boiling_group",
        skus=boiling_group_df["sku"].tolist(),
        boiling_id=boiling_group_df.iloc[0]["boiling_id"],
        boiling_model=boiling_model,
        n_tanks=n_tanks,
        group_tanks=group_tanks,
        first_tank=first_tank,
    )

    boiling_sequence = make_boiling_sequence(boiling_group_df)
    push(maker.root, boiling_sequence)
    analysis_start = listify(boiling_sequence["boiling"])[-1]["abandon"].x[0]
    with make("analysis_group", x=(analysis_start, 0), push_func=add_push):
        analysis = delistify(
            boiling_model.analysis
        )  # todo: can bge a list for some reason
        if boiling_model.flavoring_agent:
            make("analysis", size=(analysis.analysis_time // 5, 0))
            make("preparation", size=(analysis.preparation_time // 5, 0))
            make("pumping", size=(analysis.pumping_time // 5, 0))
        else:
            make("preparation", size=(analysis.preparation_time // 5, 0))
            make("analysis", size=(analysis.analysis_time // 5, 0))
            make("pumping", size=(analysis.pumping_time // 5, 0))

    # todo: add to rules
    first_packing_sku = boiling_group_df["sku"].iloc[0]
    if first_packing_sku.weight_netto != 0.5:
        packing_start = maker.root["analysis_group"]["pumping"].x[0] + 1
    else:
        packing_start = maker.root["analysis_group"]["pumping"].y[0] - 1

    # todo: pauses
    packing_time = sum(
        [
            row["kg"] / row["sku"].packing_speed * 60
            for i, row in boiling_group_df.iterrows()
        ]
    )
    packing_time = int(custom_round(packing_time, 5, "ceil", pre_round_precision=1))
    assert packing_time >= 15, "Время паковки должно превышать 15 минут"
    make(
        "packing", x=(packing_start, 0), size=(packing_time // 5, 0), push_func=add_push
    )
    return maker.root
