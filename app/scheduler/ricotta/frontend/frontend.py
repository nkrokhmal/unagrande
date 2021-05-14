from utils_ak.interactive_imports import *
from app.scheduler.time import *
from app.scheduler.frontend import *
from datetime import datetime


def make_frontend_boiling(boiling):
    boiling_label = boiling.props["boiling_model"].short_display_name

    maker, make = init_block_maker(
        "boiling",
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
        boiling_label=boiling_label,
    )

    is_pumping_parallel = boiling["pumping_out"].x[0] < boiling["abandon"].y[0]

    with make():
        boiling_name_size = boiling.size[0] - boiling["heating"].size[0]

        if is_pumping_parallel:
            boiling_name_size -= boiling["pumping_out"].size[0]

        make("boiling_num", size=(boiling["heating"].size[0], 1))
        make("boiling_name", size=(boiling_name_size, 1))

        if is_pumping_parallel:
            make("pumping_out", size=(boiling["pumping_out"].size[0], 1))

    with make():
        make("heating", size=(boiling["heating"].size[0], 1), text="1900")
        make("delay", size=(boiling["delay"].size[0], 1))
        make("protein_harvest", size=(boiling["protein_harvest"].size[0], 1))
        make("abandon", size=(boiling["abandon"].size[0], 1))

        if not is_pumping_parallel:
            make("pumping_out", size=(boiling["pumping_out"].size[0], 1))

    with make():
        make(make_steam_blocks(boiling["steam_consumption"], x=(0, 0)))

    return maker.root


def make_boiling_lines(schedule):
    maker, make = init_block_maker("boiling_lines", axis=1)

    boiling_lines = []
    for i in range(3):
        boiling_lines.append(
            make(f"boiling_line_{i}", size=(0, 3), is_parent_node=True).block
        )
        if i <= 1:
            make("stub", size=(0, 1))

    for boiling_group in listify(schedule["boiling_group"]):
        for i, line_num in enumerate(boiling_group.props["line_nums"]):
            boiling = listify(boiling_group["boiling_sequence"]["boiling"])[i]
            push(
                boiling_lines[line_num],
                make_frontend_boiling(boiling),
                push_func=add_push,
            )

    for i, cleaning in enumerate(listify(schedule["bath_cleanings"]["bath_cleaning"])):
        cleaning_block = maker.copy(cleaning, with_props=True)
        for block in cleaning_block.children:
            block.props.update(size=(block.size[0], 2))
        push(boiling_lines[i], cleaning_block, push_func=add_push)

    return maker.root


def make_analysis_line(schedule):
    maker, make = init_block_maker("analysis", size=(0, 2), axis=1, is_parent_node=True)

    validator = ClassValidator(window=1)

    def validate(b1, b2):
        for c1 in b1.children:
            for c2 in b2.children:
                validate_disjoint_by_axis(c1, c2)

    validator.add("analysis_group", "analysis_group", validate)

    n_lines = 2

    lines = []
    for i in range(n_lines):
        lines.append(
            make(f"analysis_line_{i}", size=(0, 1), is_parent_node=False).block
        )

    # todo: hardcode
    for line in lines:
        push(line, maker.create_block("stub", size=(0, 1)), push_func=add_push)

    for boiling_group in listify(schedule["boiling_group"]):
        analysis_group = maker.create_block("analysis_group")
        for block in boiling_group["analysis_group"].children:
            _block = maker.create_block(
                block.props["cls"],
                size=(block.size[0], 1),
                x=(block.x[0], 0),
            )
            push(analysis_group, _block, push_func=add_push)

        # todo: refactor
        for i, line in enumerate(lines):
            res = push(
                line,
                analysis_group,
                push_func=lambda parent, block: simple_push(
                    parent, block, validator=validator
                ),
            )
            if not isinstance(res, dict):
                # success
                break
            else:
                if i == len(lines) - 1:
                    # last one
                    raise Exception(
                        "Не получилось прорисовать баки Ришад-Ричи на двух линиях."
                    )
    return maker.root


def calc_skus_label(skus):
    values = []
    for sku in skus:
        values.append([str(sku.weight_netto), sku.brand_name])

    tree = df_to_ordered_tree(pd.DataFrame(values))
    return ", ".join(
        [
            "/".join(form_factor_labels) + " " + group_label
            for group_label, form_factor_labels in tree
        ]
    )


def make_packing_line(schedule):
    maker, make = init_block_maker("packing", size=(0, 1), is_parent_node=True)

    for boiling_group in listify(schedule["boiling_group"]):
        brand_label = calc_skus_label(boiling_group.props["skus"])

        make(
            "packing_num",
            size=(2, 1),
            x=(boiling_group["packing"].x[0], 0),
            push_func=add_push,
            boiling_id=boiling_group.props["boiling_id"],
            font_size=9,
        )

        make(
            "packing",
            size=(boiling_group["packing"].size[0] - 2, 1),
            x=(boiling_group["packing"].x[0] + 2, 0),
            push_func=add_push,
            brand_label=brand_label,
            font_size=9,
        )

    return maker.root


def make_container_cleanings(schedule):
    maker, make = init_block_maker(
        "container_cleanings", size=(0, 1), is_parent_node=True
    )

    for block in schedule["container_cleanings"].children:
        make(
            block.props["cls"],
            size=(block.size[0], 1),
            x=(block.x[0], 0),
            push_func=add_push,
        )
    return maker.root


def make_header(date, start_time="07:00"):
    maker, make = init_block_maker("header", axis=1)

    with make("header", size=(0, 1), index_width=2):
        make(size=(1, 1), text="График наливов сыворотки")
        make(size=(1, 1), text=cast_str(date, "%d.%m.%Y"), bold=True)
        for i in range(566):
            cur_time = cast_time(i + cast_t(start_time))
            days, hours, minutes = cur_time.split(":")
            if cur_time[-2:] == "00":
                make(
                    size=(1, 1),
                    text=str(int(hours)),
                    color=(218, 150, 148),
                    text_rotation=90,
                    font_size=9,
                )
            else:
                make(
                    size=(1, 1),
                    text=minutes,
                    color=(204, 255, 255),
                    text_rotation=90,
                    font_size=9,
                )
    return maker.root["header"]


def make_frontend(schedule, date=None, start_time="07:00"):
    date = date or datetime.now()

    maker, make = init_block_maker("frontend", axis=1)
    make("stub", size=(0, 1))  # start with 1
    make(make_header(date=date, start_time=start_time))
    make(make_boiling_lines(schedule))
    make(make_analysis_line(schedule))
    make(make_packing_line(schedule))
    make(make_container_cleanings(schedule))
    return maker.root