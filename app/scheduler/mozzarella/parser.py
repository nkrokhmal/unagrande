# fmt: off
from app.imports.runtime import *

from app.scheduler.mozzarella import *
from app.scheduler.mozzarella.properties import *

from utils_ak.block_tree import *


TIME_INDEX_ROW_NUMS = [1, 23]


def _group_intervals(intervals, max_length=None, interval_func=None):
    if not interval_func:
        interval_func = lambda interval: [interval[0], interval[1]]
    groups = []

    intervals = list(sorted(intervals, key=lambda interval: interval_func(interval)[0]))

    cur_group = []
    for interval in intervals:
        if not cur_group:
            cur_group.append(interval)
            continue

        if interval_func(cur_group[-1])[-1] == interval_func(interval)[0]:
            # subsequent
            cur_group.append(interval)
            if max_length and len(cur_group) == max_length:
                groups.append(cur_group)
                cur_group = []
        else:
            # gap between
            groups.append(cur_group)
            cur_group = [interval]

    if cur_group:
        groups.append(cur_group)
    return groups


def test_group_intervals():
    intervals = [[1, 2], [4, 5], [2, 4], [10, 11]]
    intervals = list(sorted(intervals, key=lambda interval: interval[0]))
    assert _group_intervals(intervals, max_length=2) == [
        [[1, 2], [2, 4]],
        [[4, 5]],
        [[10, 11]],
    ]


def load_cells_df(wb_obj):
    wb = utils.cast_workbook(wb_obj)

    with code("Get merged cells dataframe"):
        ws = wb["Расписание"]
        df = pd.DataFrame()
        df["cell"] = ws.merged_cells.ranges

        bound_names = ("x0", "x1", "y0", "y1")

        df["bounds"] = df["cell"].apply(lambda cell: cell.bounds)
        for i in range(4):
            df[bound_names[i]] = df["bounds"].apply(lambda bound: bound[i])

        df["y0"] += 1
        df["y1"] += 1
        df["label"] = df["cell"].apply(lambda cell: cell.start_cell.value)

        df = df.sort_values(by=["x1", "x0", "y1", "y0"])
    return df

def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj)

    m = BlockMaker("root")

    def parse_block(label, element_label, rows, start_time, length=2):
        with m.row(label, x=start_time, push_func=add_push):
            for i, row_num in enumerate(rows):
                df1 = df[(df["x1"] == row_num) & (df["x0"] >= 4)] # filter column header
                groups = _group_intervals(
                    [row for i, row in df1.iterrows()],
                    max_length=length,
                    interval_func=lambda row: [row["x0"], row["y0"]],
                )

                for group in groups:
                    try:
                        boiling_id = int(group[0]["label"].split(" ")[0])
                    except Exception as e:
                        boiling_id = None

                    m.row(
                        element_label,
                        size=group[-1]["y0"] - group[0]["x0"],
                        x=group[0]["x0"] - 5,  # subtract column header
                        boiling_id=boiling_id,
                        line_num=str(i),
                        group=group,
                        label=str(boiling_id),
                        push_func=add_push,
                    )

    with code("fetch start times"):
        start_times = []

        for row_num in TIME_INDEX_ROW_NUMS:
            hour = int(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"])
            if hour >= 12:
                # yesterday
                hour -= 24
            start_times.append(hour * 12)

    with code('calc split rows'):
        with code('find headers'):
            df1 = df[df['x0'] >= 5]  # column header out

            cheese_maker_headers = []
            water_melting_headers = []
            salt_melting_headers = []
            headers = []

            for row_num in df1['x1'].unique():
                row_labels = [row['label'] for i, row in df1[df1['x1'] == row_num].iterrows()]
                row_labels = [re.sub(r'\s+', ' ', label) for label in row_labels if label]

                if {'налив/внесение закваски', 'схватка'}.issubset(set(row_labels)):
                    cheese_maker_headers.append(row_num - 1)

                if set(row_labels) == {'подача и вымешивание'}:
                    water_melting_headers.append(row_num + 1)

                if set(row_labels) == {'подача и вымешивание', 'посолка', 'плавление/формирование'}:
                    salt_melting_headers.append(row_num - 1)

                with code('find all headers'):
                    _labels = [label.replace('налив', '') for label in row_labels]
                    _labels = [re.sub(r'\s+', '', label) for label in _labels]
                    int_labels = [int(label) for label in _labels if utils.is_int_like(label)]

                    if not ('05' in row_labels and '55' in row_labels):
                        # not a time header
                        if int_labels:
                            headers.append(row_num)

            packing_headers = set(headers) - set(cheese_maker_headers) - set(water_melting_headers) - set(
                salt_melting_headers)
            packing_headers = list(sorted(packing_headers))[:2]

        split_rows = []
        split_rows.append(cheese_maker_headers[-1] - 16)

        if water_melting_headers:
            # water present
            split_rows.append(water_melting_headers[0] - 1)
            split_rows.append(packing_headers[0])
            packing_headers = packing_headers[1:]
        else:
            split_rows += [None, None]

        if salt_melting_headers:
            # salt present
            split_rows.append(salt_melting_headers[0])
            split_rows.append(packing_headers[0])
        else:
            split_rows += [None, None]


    parse_block(
        "boilings",
        "boiling",
        [split_rows[0] + i for i in [0, 4, 12, 16]],
        start_times[0],
    )
    parse_block("cleanings", "cleaning", [split_rows[0] + 8], start_times[0])
    if water_melting_headers:
        parse_block("water_meltings", "melting", [split_rows[1] + 1], start_times[1])

        # todo maybe: make properly
        with code('meta info to water meltings'):
            with code('melting_end'):
                for melting in m.root['water_meltings'].children:
                    melting.props.update(melting_end=melting.y[0])

            with code('melting_end_with_cooling'):
                df_formings = df[df["label"] == "охлаждение"]

                with code("fix start times and column header"):
                    df_formings["x0"] += start_times[1] - 5
                    df_formings["y0"] += start_times[1] - 5
                    df_formings["x1"] += start_times[1] - 5
                    df_formings["y1"] += start_times[1] - 5

                df_formings = df_formings.sort_values(by="x0")
                for i, row in df_formings.iterrows():
                    overlapping = [
                        m
                        for m in m.root["water_meltings"].children
                        if calc_interval_length(cast_interval(m.x[0], m.y[0]) & cast_interval(row['x0'], row['y0'])) > 0
                    ]
                    if not overlapping:
                        # first cooling in each boiling does not qualify the filter
                        continue

                    melting = utils.delistify(overlapping, single=True)
                    cooling_length = row['y0'] - melting.x[0]
                    melting.props.update(melting_end_with_cooling=melting.y[0] + cooling_length)

        parse_block("water_packings", "packing", [split_rows[1] + 7], start_times[1])

    if salt_melting_headers:
        with code("Find rows for salt melting lines"):
            last_melting_row = df[df["label"] == "посолка"]["x1"].max()
            salt_melting_rows = list(range(split_rows[3], last_melting_row, 4))

        parse_block("salt_meltings", "melting", salt_melting_rows, start_times[1])

        # todo maybe: make properly
        with code("add salt forming info to meltings"):
            df_formings = df[
                (df["label"] == "плавление/формирование") & (df["x1"] >= split_rows[3])
            ]

            df_formings['serving_start'] = df_formings['x0'].apply(lambda x0: df[(df['y0'] == x0) & (df['label'] == 'подача и вымешивание')].iloc[0]['x0'])

            with code("fix start times and column header"):
                df_formings["x0"] += start_times[1] - 5
                df_formings["y0"] += start_times[1] - 5
                df_formings["x1"] += start_times[1] - 5
                df_formings["y1"] += start_times[1] - 5
                df_formings["serving_start"] += start_times[1] - 5

            df_formings = df_formings.sort_values(by="x0")

            for i, row in df_formings.iterrows():
                melting = utils.delistify([m for m in m.root["salt_meltings"].children if m.x[0] == row['serving_start']], single=True)
                melting.props.update(melting_start=row['x0'],
                                     melting_end=row["y0"],
                                     melting_end_with_cooling=melting.y[0])

        parse_block(
            "salt_packings",
            "packing",
            [split_rows[4], split_rows[4] + 6],
            start_times[1],
        )
    return m.root


def prepare_boiling_plan(parsed_schedule, df_bp):
    df_bp["line_name"] = df_bp["line"].apply(lambda line: line.name)

    for line_name, grp_line in df_bp.groupby("line_name"):
        if line_name == LineName.WATER:
            boiling_ids = [b.props["label"] for b in parsed_schedule["water_packings"].children]
        else:
            boiling_ids = [b.props["label"] for b in parsed_schedule["salt_packings"].children]
        boiling_ids = list(sorted(set(boiling_ids)))
        for i, (_, grp) in enumerate(grp_line.groupby("group_id")):
            df_bp.loc[grp.index, "boiling_id"] = boiling_ids[i]
    df_bp["boiling_id"] = df_bp["boiling_id"].astype(int)
    return df_bp


def fill_properties(parsed_schedule, df_bp):
    props = MozzarellaProperties()

    # save boiling_model to parsed_schedule blocks
    for block in list(parsed_schedule.iter(
        cls=lambda cls: cls in ["boiling", "melting", "packing"]
    )):
        # todo later: make that should not happen and then del
        with code('remove little blocks'):
            if 'boiling_id' not in block.props.all() or not is_int(block.props['boiling_id']):
                logger.info('Removing small block', block=block)
                block.detach_from_parent()
                continue

        boiling_group_df = df_bp[df_bp["boiling_id"] == int(block.props["boiling_id"])]
        block.props.update(
            boiling_group_df=boiling_group_df,
            line_name=boiling_group_df.iloc[0]["boiling"].line.name,
            boiling_model=boiling_group_df.iloc[0]["boiling"],
        )

    # parse boilings
    boilings = parsed_schedule["boilings"]["boiling", True]
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))
    salt_boilings = [b for b in boilings if b.props["line_name"] == LineName.SALT]
    salt_boilings = list(sorted(salt_boilings, key=lambda b: b.x[0]))
    water_boilings = [b for b in boilings if b.props["line_name"] == LineName.WATER]
    water_boilings = list(sorted(water_boilings, key=lambda b: b.x[0]))

    # filling code is mirroring the pickle parser from app/scheduler/mozzarella/properties.py

    props.bar12_present = "1.2" in [sku.form_factor.name for sku in df_bp["sku"]]

    with code("2.7, 3.3, 3.6 tanks"):
        _boilings = [b for b in boilings if str(b.props["boiling_model"].percent) == "3.3"]
        if _boilings:
            _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
            props.line33_last_termizator_end_times = [cast_human_time(b.x[0] + (b.props["group"][0]["y0"] - b.props["group"][0]["x0"])) for b in _tank_boilings]

        _boilings = [b for b in boilings if str(b.props["boiling_model"].percent) == "3.6"]
        if _boilings:
            _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
            props.line36_last_termizator_end_times = [cast_human_time(b.x[0] + (b.props["group"][0]["y0"] - b.props["group"][0]["x0"])) for b in _tank_boilings]

        _boilings = [b for b in boilings if str(b.props["boiling_model"].percent) == "2.7"]
        if _boilings:
            _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
            props.line27_last_termizator_end_times = [cast_human_time(b.x[0] + (b.props["group"][0]["y0"] - b.props["group"][0]["x0"])) for b in _tank_boilings]

    with code("multihead"):
        multihead_packings = list(
            parsed_schedule.iter(
                cls="packing",
                boiling_group_df=lambda df: df["sku"].iloc[0].packers[0].name
                == "Мультиголова",
            )
        )
        if multihead_packings:
            props.multihead_end_time = cast_human_time(
                max(packing.y[0] for packing in multihead_packings)
            )

        water_multihead_packings = list(
            parsed_schedule.iter(
                cls="packing",
                boiling_group_df=lambda df: df["sku"].iloc[0].packers[0].name
                == "Мультиголова"
                and df.iloc[0]["boiling"].line.name == LineName.WATER,
            )
        )
        if water_multihead_packings:
            props.water_multihead_present = True

    with code("cleanings"):
        props.short_cleaning_times = [
            cast_human_time(cleaning.x[0])
            for cleaning in parsed_schedule.iter(cls="cleaning")
            if "Короткая мойка" in cleaning.props["group"][0]["label"]
        ]
        props.full_cleaning_times = [
            cast_human_time(cleaning.x[0])
            for cleaning in parsed_schedule.iter(cls="cleaning")
            if "Полная мойка" in cleaning.props["group"][0]["label"]
        ]

    with code("meltings"):
        if salt_boilings:
            props.salt_melting_start_time = cast_human_time(parsed_schedule["salt_meltings"]["melting", True][0].props['melting_start'])

    with code("cheesemakers"):
        values = []
        for b in parsed_schedule["boilings"]["boiling", True]:
            values.append([b.props["line_num"], b.y[0]])

        df1 = pd.DataFrame(values, columns=["pouring_line", "finish"])
        values = df1.groupby("pouring_line").agg(max).to_dict()["finish"]
        values = list(
            sorted(values.items(), key=lambda kv: kv[0])
        )  # [('0', 116), ('1', 97), ('2', 149), ('3', 160)]
        values_dict = dict(values)
        props.cheesemaker1_end_time = cast_human_time(values_dict.get("0"))
        props.cheesemaker2_end_time = cast_human_time(values_dict.get("1"))
        props.cheesemaker3_end_time = cast_human_time(values_dict.get("2"))
        props.cheesemaker4_end_time = cast_human_time(values_dict.get("3"))

    with code("melting end"):

        def _get_melting_end(line_boilings):
            if not line_boilings:
                return None
            line_boilings = list(sorted(line_boilings, key=lambda b: b.x[0]))
            last_boiling_id = line_boilings[-1].props["boiling_id"]
            last_melting = parsed_schedule.find_one(cls="melting", boiling_id=last_boiling_id)
            return last_melting.props['melting_end_with_cooling']

        props.water_melting_end_time = cast_human_time(_get_melting_end(water_boilings))
        props.salt_melting_end_time = cast_human_time(_get_melting_end(salt_boilings))

    with code("drenators"):
        with code("fill drenators info"):
            for line_num in range(4):
                line_boilings = [
                    b for b in boilings if b.props["line_num"] == str(line_num)
                ]
                line_boilings = list(sorted(line_boilings, key=lambda b: b.x[0]))

                cur_drenator_num = -1
                for b1, b2 in utils.iter_pairs(line_boilings, method='any_prefix'):

                    if not b1:
                        cur_drenator_num += 1
                    else:
                        melting = parsed_schedule.find_one(cls='melting', boiling_id=b1.props['boiling_id'])
                        if b2.y[0] - 5 < melting.props["melting_end"]: # todo later: make pouring off properly
                            cur_drenator_num += 1
                        else:
                            # use same drenator for the next boiling
                            pass
                    b2.props.update(drenator_num=cur_drenator_num % 2,
                                    drenator_end=b2.y[0] + b2.props["boiling_model"].line.chedderization_time // 5 - 5)  # todo later: make pouring off properly


        with code("fill drenator properties"):
            # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
            values = []
            for boiling in boilings:
                values.append(
                    [
                        boiling.props["drenator_end"],
                        boiling.props["line_num"],
                        boiling.props["drenator_num"],
                    ]
                )
            df = pd.DataFrame(values, columns=["drenator_end", "pouring_line", "drenator_num"])
            df["id"] = df["pouring_line"].astype(int) * 2 + df["drenator_num"].astype(int)
            df = df[["id", "drenator_end"]]
            df = df.drop_duplicates(subset="id", keep="last")
            df = df.reset_index(drop=True)
            df["id"] = df["id"].astype(int) + 1

            df = df.sort_values(by="id")

            values = df.values.tolist()
            values_dict = dict(values)
            props.drenator1_end_time = cast_human_time(values_dict.get(1))
            props.drenator2_end_time = cast_human_time(values_dict.get(2))
            props.drenator3_end_time = cast_human_time(values_dict.get(3))
            props.drenator4_end_time = cast_human_time(values_dict.get(4))
            props.drenator5_end_time = cast_human_time(values_dict.get(5))
            props.drenator6_end_time = cast_human_time(values_dict.get(6))
            props.drenator7_end_time = cast_human_time(values_dict.get(7))
            props.drenator8_end_time = cast_human_time(values_dict.get(8))

    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    df_bp = read_boiling_plan(fn)
    df_bp = prepare_boiling_plan(parsed_schedule, df_bp)
    props = fill_properties(parsed_schedule, df_bp)
    return props


if __name__ == "__main__":
    fn = "/Users/marklidenberg/Desktop/2021-09-04 Расписание моцарелла.xlsx"
    print(dict(parse_properties(fn)))
