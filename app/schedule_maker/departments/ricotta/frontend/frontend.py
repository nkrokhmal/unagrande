from utils_ak.block_tree import *
from utils_ak.builtin import *


def make_frontend_boiling(boiling):
    maker, make = init_block_maker(
        "boiling",
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 3),
        boiling_id=boiling.props["boiling_id"],
        boiling_label=boiling.props["boiling_label"],
    )

    with make():
        make("boiling_num", size=(boiling["heating"].size[0], 1))
        make("boiling_name", size=(boiling.size[0] - boiling["heating"].size[0], 1))

    with make():
        make("heating", size=(boiling["heating"].size[0], 1), text="1900")
        make("delay", size=(boiling["delay"].size[0], 1))
        make("protein_harvest", size=(boiling["protein_harvest"].size[0], 1))
        make("abandon", size=(boiling["abandon"].size[0], 1))
        make("pumping_out", size=(boiling["pumping_out"].size[0], 1))
    return maker.root


def make_frontend(schedule):
    maker, make = init_block_maker("frontend", axis=1)
    make("stub", size=(0, 1))  # start with 1

    boiling_lines = []
    for i in range(3):
        boiling_lines.append(
            make(f"boiling_line_{i}", size=(0, 3), is_parent_node=True).block
        )
        make("stub", size=(0, 2))

    for boiling_group in listify(schedule["boiling_group"]):
        for i, line_num in enumerate(boiling_group.props["line_nums"]):
            boiling = listify(boiling_group["boiling_sequence"]["boiling"])[i]
            push(boiling_lines[line_num], make_frontend_boiling(boiling))
    return maker.root
