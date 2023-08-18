from utils_ak.block_tree import *

from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from app.scheduler.time import *


def wrap_boiling_lines(schedule):
    m = BlockMaker(
        "line",
        default_row_width=1,
        default_col_width=1,
        # props
        font_size=9,
        axis=1,
    )

    with code("Init lines"):
        boiling_lines = []
        boiling_line = m.block("boiling_line_1", size=(0, 2)).block
        boiling_lines.append(boiling_line)
        boiling_line = m.block("boiling_line_2", size=(0, 2)).block
        boiling_lines.append(boiling_line)
        # m.row("stub", size=0, boiling_line=boiling_line) # create  reference for upper boiling line in stub

    for child in schedule.iter(cls=lambda cls: cls in ["preparation", "displacement", "cleaning"]):
        if not child.is_leaf():
            continue
        block = _wrap_child(child).children[0]
        push(
            boiling_lines[0],
            block,
            push_func=simple_push,
            validator=disjoint_validator,
        )

    for child in schedule.iter(cls=lambda cls: cls == "boiling"):
        block = _wrap_boiling(child)

        for i in range(len(boiling_lines)):
            push(
                boiling_lines[child.props["tank_number"]],
                block,
                push_func=add_push,
            )
    return m.root


def _wrap_child(child):
    m = BlockMaker(
        "butter_block",
        default_row_width=1,
        default_col_width=2,
        # props
        axis=0,
        tank_number=child.props.get("tank_number"),
    )

    child.update_size(size=(child.size[0], 2))

    if child.props["cls"] == "pasteurization":
        with m.block(
            "pasteurization", push_func=add_push, x=(child.x[0], 0), boiling_model=child.props["boiling_model"]
        ):
            m.block("pasteurization_1", push_func=add_push, size=(child.size[0], 1), x=(0, 0))

            m.block("pasteurization_2", push_func=add_push, size=(child.size[0], 1), x=(0, 1))
    else:
        m.row(m.copy(child, with_props=True), push_func=add_push)

    return m.root


def _wrap_boiling(boiling):
    m = BlockMaker(
        "boiling",
        default_row_width=1,
        default_col_width=2,
        # props
        axis=0,
    )

    for child in boiling.iter():
        child.update_size(size=(child.size[0], 2))

        if child.props["cls"] == "pasteurization":
            with m.block(
                "pasteurization", push_func=add_push, x=(child.x[0], 0), boiling_model=child.props["boiling_model"]
            ):
                m.block("pasteurization_1", push_func=add_push, size=(child.size[0], 1), x=(0, 0))

                m.block("pasteurization_2", push_func=add_push, size=(child.size[0], 1), x=(0, 1))
        else:
            m.row(m.copy(child, with_props=True), push_func=add_push)

    return m.root


def wrap_packing(schedule):
    m = BlockMaker(
        "line",
        default_row_width=1,
        default_col_width=1,
        # props
        font_size=9,
    )
    for child_prev, child in utils.iter_pairs(list(schedule.iter(cls="packing")), method="any_prefix"):
        child.update_size(size=(child.size[0], 2))
        if child_prev:
            m.block("cooling", size=(4, 2), x=(child.x[0] - 4, 0), push_func=add_push)

        m.row(m.copy(child, with_props=True), push_func=add_push)
    return m.root


def wrap_frontend(schedule, date=None):
    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1

    # calc start time
    start_t = int(utils.custom_round(schedule.x[0], 12, "floor"))  # round to last hour
    start_time = cast_time(start_t)

    m.block(wrap_header(date=date, start_time=start_time, header="График работы маслоцеха"))
    with m.block(start_time=start_time, axis=1):
        m.block(wrap_boiling_lines(schedule))

    with m.block(start_time=start_time, axis=1):
        m.block(wrap_packing(schedule))
    return m.root
