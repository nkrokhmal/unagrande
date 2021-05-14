from app.imports.runtime import *
from app.models import *


def make_cream_cheese_boiling(boiling_group_df, **props):
    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]

    boiling_id = boiling_group_df.iloc[0]["boiling_id"]
    maker, make = utils.init_block_maker(
        "cream_cheese_boiling",
        boiling_model=boiling_model,
        boiling_id=boiling_id,
        **props
    )

    bt = utils.delistify(boiling_model.boiling_technologies, single=True)

    with make("boiling_process"):
        make("cooling", size=(bt.cooling_time // 5, 0))
        make("separation", size=(bt.separation_time // 5, 0))
        make("salting", size=(bt.salting_time // 5, 0))
        make("separation", size=(bt.separation_time // 5, 0))
        make("salting", size=(bt.salting_time // 5, 0))
        make("P", size=(bt.p_time // 5, 0))
    with make(
        "packing_process",
        x=(maker.root["boiling_process"]["separation"][-1].x[0] - bt.p_time // 5, 0),
        push_func=utils.add_push,
    ):
        make("P", size=(bt.p_time // 5, 0))
        packing_time = sum(
            [
                row["kg"] / row["sku"].packing_speed * 60
                for i, row in boiling_group_df.iterrows()
            ]
        )
        packing_time = int(
            utils.custom_round(packing_time, 5, "ceil", pre_round_precision=1)
        )
        make(
            "packing",
            size=(packing_time // 5, 0),
        )
    return maker.root