# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *


class MozzarellaProperties(pydantic.BaseModel):
    bar12_present: bool = False
    line33_last_termizator_end_time: str = ""
    line36_last_termizator_end_time: str = ""
    line27_nine_termizator_end_time: str = ""
    line27_last_termizator_end_time: str = ""
    multihead_end_time: str = ''
    water_multihead_present: bool = True

    short_cleaning_times: List[str] = []
    full_cleaning_times: List[str] = []

    salt_melting_start_time: str = ''

    cheesemaker1_end_time: str = ''
    cheesemaker2_end_time: str = ''
    cheesemaker3_end_time: str = ''
    cheesemaker4_end_time: str = ''

    water_melting_end_time: str = ''
    salt_melting_end_time: str = ''

    drenator1_end_time: str = ''
    drenator2_end_time: str = ''
    drenator3_end_time: str = ''
    drenator4_end_time: str = ''
    drenator5_end_time: str = ''
    drenator6_end_time: str = ''
    drenator7_end_time: str = ''
    drenator8_end_time: str = ''


def parse_schedule(schedule):
    props = MozzarellaProperties()

    with code("bar12_present"):
        skus = sum(
            [
                list(b.props["boiling_group_df"]["sku"])
                for b in schedule["master"]["boiling", True]
            ],
            [],
        )
        props.bar12_present = "1.2" in [sku.form_factor.name for sku in skus]

    with code('2.7, 3.3, 3.6 tanks'):
        boilings = schedule['master']['boiling', True]

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '3.3']
        props.line33_last_termizator_end_time = cast_time(_boilings[-1]['pouring']['first']['termizator'].y[0])

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '3.6']
        props.line36_last_termizator_end_time = cast_time(_boilings[-1]['pouring']['first']['termizator'].y[0])

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '2.7']
        if len(_boilings) >= 10:
            props.line27_nine_termizator_end_time = cast_time(_boilings[8]['pouring']['first']['termizator'].y[0])
        props.line27_last_termizator_end_time = cast_time(_boilings[-1]['pouring']['first']['termizator'].y[0])

    with code('multihead'):
        multihead_packings = list(schedule.iter(cls='packing', boiling_group_df=lambda df: df['sku'].iloc[0].packers[0].name == 'Мультиголова'))
        if multihead_packings:
            props.multihead_end_time = max(packing.y[0] for packing in multihead_packings)

        water_multihead_packings = list(schedule.iter(cls='packing', boiling_group_df=lambda df: df['sku'].iloc[0].packers[0].name == 'Мультиголова' and df.iloc[0]['boiling'].line.name == LineName.WATER))
        if water_multihead_packings:
            props.water_multihead_present = True

    with code('cleanings'):
        props.short_cleaning_times = [cast_time(cleaning.x[0]) for cleaning in schedule['master']['cleaning', True] if cleaning.props['cleaning_type'] == 'short']
        props.full_cleaning_times = [cast_time(cleaning.x[0]) for cleaning in schedule['master']['cleaning', True] if cleaning.props['cleaning_type'] == 'full']

    with code('meltings'):
        salt_boilings = [b for b in schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']
        if salt_boilings:
            props.salt_melting_start_time = cast_time(salt_boilings[0]['melting_and_packing']['melting']['meltings'].x[0])

    with code('cheesemakers'):
        values = []
        for b in schedule['master']['boiling', True]:
            values.append([b.props['pouring_line'], b['pouring'].y[0]])
        df = pd.DataFrame(values, columns=['pouring_line', 'finish'])
        values = df.groupby('pouring_line').agg(max).to_dict()['finish']
        values = list(sorted(values.items(), key=lambda kv: kv[0]))  # [('0', 116), ('1', 97), ('2', 149), ('3', 160)]

        props.cheesemaker1_end_time = cast_time(values[0][1])
        props.cheesemaker2_end_time = cast_time(values[1][1])
        props.cheesemaker3_end_time = cast_time(values[2][1])
        props.cheesemaker4_end_time = cast_time(values[3][1])

    with code('melting end'):
        lines_df = pd.DataFrame(index=['water', 'salt'])
        lines_df['boilings'] = None
        lines_df.loc['water', 'boilings'] = [b for b in schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Моцарелла в воде']
        lines_df.loc['salt', 'boilings'] = [b for b in schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']
        lines_df['melting_end'] = lines_df['boilings'].apply(lambda boilings: None if not boilings else boilings[-1]['melting_and_packing']['melting'].y[0])
        props.water_melting_end_time = cast_time(lines_df.loc['water', 'melting_end'])
        props.salt_melting_end_time = cast_time(lines_df.loc['salt', 'melting_end'])

    with code('drenators'):
        # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
        values = []
        for boiling in schedule['master']['boiling', True]:
            drenator = boiling['drenator']
            values.append([drenator.y[0], drenator.props['pouring_line'], drenator.props['drenator_num']])
        df = pd.DataFrame(values, columns=['drenator_end', 'pouring_line', 'drenator_num'])
        df['id'] = df['pouring_line'].astype(int) * 2 + df['drenator_num'].astype(int)
        df = df[['id', 'drenator_end']]
        df = df.drop_duplicates(subset='id', keep='last')
        df = df.reset_index(drop=True)
        df['id'] = df['id'].astype(int) + 1

        df = df.sort_values(by='id')

        values = df.values.tolist()

        props.drenator1_end_time = cast_time(values[0][1])
        props.drenator2_end_time = cast_time(values[1][1])
        props.drenator3_end_time = cast_time(values[2][1])
        props.drenator4_end_time = cast_time(values[3][1])
        props.drenator5_end_time = cast_time(values[4][1])
        props.drenator6_end_time = cast_time(values[5][1])
        props.drenator7_end_time = cast_time(values[6][1])
        props.drenator8_end_time = cast_time(values[7][1])

    return dict(props)
