# fmt: off
from app.imports.runtime import *
from utils_ak.block_tree import *
from app.scheduler.time import *
from app.enum import *


# todo maybe: put into more proper place
def calc_scotta_input_tanks(n_boilings, extra_scotta=0):
    scotta_per_boiling = 1900 - 130
    values = [['4', 80000], ['5', 80000], ['8', 80000]]
    tanks_df = pd.DataFrame(values, columns=['id', 'kg'])
    tanks_df['max_boilings'] = tanks_df['kg'].apply(
        lambda kg: int(custom_round(kg / scotta_per_boiling, 1, rounding='floor')))
    tanks_df['n_boilings'] = None
    tanks_df['scotta'] = None

    total_scotta = n_boilings * scotta_per_boiling + extra_scotta

    left_scotta = total_scotta

    assert n_boilings <= tanks_df['max_boilings'].sum(), 'Слишком много варок на линии рикотты. Скотта не помещается в танки.'
    for i, row in tanks_df.iterrows():
        if not left_scotta:
            break

        max_scotta = row['max_boilings'] * scotta_per_boiling
        cur_scotta = min(max_scotta, left_scotta)
        left_scotta -= cur_scotta

        tanks_df.loc[i, 'scotta'] = cur_scotta

    tanks_df = tanks_df.fillna(0)
    tanks_df['scotta'] /= 1000.
    return tanks_df[['id', 'scotta']].values.tolist()


class CleaningValidator(ClassValidator):
    def __init__(self, window=30, ordered=True):
        self.ordered = ordered
        super().__init__(window=window)

    def validate__cleaning__cleaning(self, b1, b2):
        validate_disjoint_by_axis(b1, b2, distance=2, ordered=self.ordered)


def run_order(function_or_generators, order):
    for i in order:
        obj = function_or_generators[i]
        if callable(obj):
            obj()
        elif isinstance(obj, types.GeneratorType):
            next(obj)


def _make_contour_1(schedules, properties, order=(0, 1, 2), shipping_line=True):
    m = BlockMaker("1 contour")
    if shipping_line:
        m.row('cleaning', push_func=add_push,
              size=cast_t('01:20'), x=cast_t('06:30'),
              label='Линиия отгрузки')

    m.row('cleaning', push_func=AxisPusher(start_from=cast_t('08:00'), validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия приемки молока 1 + проверить фильтр')

    with code('Tanks'):
        # get values when different percentage tanks end: [['3.6', 74], ['3.3', 94], ['2.7', 144]]
        values = []
        for percent in ['2.7', '3.3', '3.6']:
            if properties['mozzarella'].termizator_times()[percent]['last']:
                values.append([percent, properties['mozzarella'].termizator_times()[percent]['last'], '01:50', False])
                values.append([percent, properties['mozzarella'].termizator_times()[percent].get('ninth'), '01:50', False])
            else:
                # no boilings found today
                values.append([percent, '10:00', '01:05', True])

        # filter empty values
        values = [value for value in values if value[1]]

        # convert time to t
        for value in values:
            value[1] = cast_t(value[1])

        df = pd.DataFrame(values, columns=['percent', 'pouring_end', 'time', 'is_short'])
        df = df[['percent', 'pouring_end', 'time', 'is_short']]
        df = df.sort_values(by='pouring_end')
        values = df.values.tolist()

        for percent, end, time, is_short in values:
            label = f'Танк смесей {percent}' if not is_short else f'Танк смесей {percent} (кор. мойка)'
            m.row('cleaning', push_func=AxisPusher(start_from=end, validator=CleaningValidator(ordered=False)),
                  size=cast_t(time),
                  label=label)

    if shipping_line:
        m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
              size=cast_t('01:20'),
              label='Линия отгрузки')

    def f1():
        if 'adygea' in schedules:
            m.row('cleaning', push_func=AxisPusher(start_from=cast_t(properties['adygea'].end_time), validator=CleaningValidator()),
                  size=cast_t('01:50'),
                  label='Линия адыгейского')

    def f2():
        if 'milk_project' in schedules:
            m.row('cleaning',
                  push_func=AxisPusher(start_from=[cast_t(properties['milk_project'].end_time), cast_t(properties['adygea'].end_time)], validator=CleaningValidator()),
                  size=cast_t('02:20'),
                  label='Милкпроджект')

    def f3():
        if 'milk_project' in schedules:
            m.row('cleaning', push_func=AxisPusher(start_from=cast_t(properties['milk_project'].end_time), validator=CleaningValidator(ordered=False)),
                  size=cast_t('01:20'),
                  label='Танк роникс')

    run_order([f1, f2, f3], order)

    for _ in range(3):
        m.row('cleaning', push_func=AxisPusher(start_from=0, validator=CleaningValidator(ordered=False)),
              size=cast_t('01:50'),
              label='Танк сырого молока')

    for _ in range(2):
        m.row('cleaning', push_func=AxisPusher(start_from=0, validator=CleaningValidator(ordered=False)),
              size=cast_t('01:50'),
              label='Танк обрата')

    return m.root


def make_contour_1(schedules, properties, *args, **kwargs):
    df = utils.optimize(_make_contour_1, lambda b: -b.y[0], schedules, properties, *args, **kwargs)
    return df.iloc[-1]['output']


def make_contour_2(schedules, properties):
    m = BlockMaker("2 contour")
    m.row('cleaning', push_func=add_push,
          size=cast_t('01:20'), x=cast_t('12:00'),
          label='Линия обрата в сливки')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Сливки от пастера 25')

    with code('Мультиголова'):
        if properties['mozzarella'].multihead_end_time:
            multihead_end = cast_t(properties['mozzarella'].multihead_end_time) + 12
            m.row('cleaning', push_func=AxisPusher(start_from=['last_end', multihead_end], validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label='Комет')

        if properties['mozzarella'].water_multihead_present:
            m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label='Фасовочная вода')

    m.row('cleaning', push_func=AxisPusher(start_from=cast_t('1:04:00'), validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Танк ЖВиКС 1')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Танк ЖВиКС 2')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Жирная вода на сепаратор')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Сливки от сепаратора жирной воды')

    return m.root


def _make_contour_3(schedules, properties, order1=(0, 1, 1, 1, 1), order2=(0, 0, 0, 0, 0, 1), is_bar12_present=False):
    m = BlockMaker("3 contour")

    for cleaning_time in properties['mozzarella'].short_cleaning_times:
        m.row('cleaning', push_func=add_push,
              size=cast_t('00:40'),
              x=cast_t(cleaning_time),
              label='Короткая мойка термизатора')

    for cleaning_time in properties['mozzarella'].full_cleaning_times:
        m.row('cleaning', push_func=add_push,
              size=cast_t('01:20'),
              x=cast_t(cleaning_time),
              label='Полная мойка термизатора')

    def f1():
        if properties['mozzarella'].salt_melting_start_time:
            m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator(ordered=False), start_from=cast_t(properties['mozzarella'].salt_melting_start_time) + 6),
                  size=90 // 5,
                  label='Контур циркуляции рассола')

    def g2():
        with code('cheese_makers'):
            # get when cheese makers end (values -> [('1', 97), ('0', 116), ('2', 149), ('3', 160)])
            values = properties['mozzarella'].cheesemaker_times()

            # convert time to t
            for value in values:
                value[0] = str(value[0])
                value[1] = cast_t(value[1])
            values = list(sorted(values, key=lambda value: value[1]))

            for n, cheese_maker_end in values:
                m.row('cleaning', push_func=AxisPusher(start_from=cheese_maker_end, validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:20'),
                      label=f'Сыроизготовитель {int(n)}')
                yield

            used_ids = set([value[0] for value in values])

        with code('non-used cheesemakers'):
            non_used_ids = set([str(x) for x in range(1, 5)]) - used_ids
            for id in non_used_ids:
                m.row('cleaning', push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:05'),
                      label=f'Сыроизготовитель {int(id)} (кор. мойка)')
                yield

    run_order([f1, g2()], order1)

    def g3():
        with code('melters_and_baths'):
            lines_df = pd.DataFrame(index=['water', 'salt'])
            lines_df['cleanings'] = [[] for _ in range(2)]
            if properties['mozzarella'].water_melting_end_time:
                lines_df.loc['water', 'cleanings'].extend([m.create_block('cleaning',
                                                                          size=(cast_t('02:20'), 0),
                                                                          label='Линия 1 плавилка'),
                                                           m.create_block('cleaning',
                                                                          size=(cast_t('01:30'), 0),
                                                                          label='Линия 1 ванна 1 + ванна 2')])
            else:
                # no water used
                m.row('cleaning', push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:45'),
                      label=f'Линия 1 плавилка (кор. мойка)')
                m.row('cleaning', push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:15'),
                      label=f'Линия 1 ванна 1 + ванна 2 (кор. мойка)')

            if properties['mozzarella'].salt_melting_end_time:
                lines_df.loc['salt', 'cleanings'].extend([m.create_block('cleaning',
                                                                         size=(cast_t('02:20'), 0),
                                                                         label='Линия 2 плавилка'),
                                                          m.create_block('cleaning',
                                                                         size=(cast_t('01:30'), 0),
                                                                         label='Линия 2 ванна 1'),
                                                          m.create_block('cleaning',
                                                                         size=(cast_t('01:30'), 0),
                                                                         label='Линия 2 ванна 2')])
            else:
                # no salt used
                m.row('cleaning',
                      push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:45'),
                      label=f'Линия 2 плавилка (кор. мойка)')
                m.row('cleaning',
                      push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:15'),
                      label=f'Линия 2 ванна 1 (кор. мойка)')
                m.row('cleaning',
                      push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:15'),
                      label=f'Линия 2 ванна 2 (кор. мойка)')

            lines_df['melting_end'] = [cast_t(properties['mozzarella'].water_melting_end_time),
                                       cast_t(properties['mozzarella'].salt_melting_end_time)]
            lines_df = lines_df.sort_values(by='melting_end')

            for i, row in lines_df.iterrows():
                for j, c in enumerate(row['cleanings']):
                    if j == 0:
                        m.block(c, push_func=AxisPusher(start_from=['last_end', row['melting_end'] + 12], validator=CleaningValidator())) # add hour
                    else:
                        m.block(c, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))
                    yield

            # make iterator longer
            for _ in range(5):
                yield

    def f4():
        b = m.row('cleaning',  push_func=AxisPusher(start_from=cast_t('21:00'), validator=CleaningValidator()),
              size=cast_t('01:00'),
              label='Короткая мойка термизатора').block
        assert cast_t('21:00') <= b.x[0] and b.y[0] <= cast_t('01:00:00'), "Short cleaning too bad"
    run_order([g3(), f4], order2)

    # shift short cleaning to make it as late as possible
    short_cleaning = m.root.find(label='Короткая мойка термизатора')[-1]
    short_cleaning.detach_from_parent()
    push(
        m.root,
        short_cleaning,
        push_func=ShiftPusher(period=-1, start_from=cast_t('01:00:00')),
        validator=CleaningValidator(ordered=False),
    )

    if is_bar12_present:
        m.row('cleaning', push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()),
              size=cast_t('01:20'),
              label='Формовщик')

    return m.root


def make_contour_3(schedules, properties, **kwargs):
    df = utils.optimize(_make_contour_3, lambda b: (-b.y[0], -b.find_one(label='Короткая мойка термизатора').x[0]), schedules, properties, **kwargs)
    return df.iloc[-1]['output']


def make_contour_4(schedules, properties, is_tomorrow_day_off=False):
    m = BlockMaker("4 contour")

    with code('drenators'):

        def _make_drenators(values, cleaning_time, label_suffix='', force_pairs=False):
            # logic
            i = 0
            while i < len(values):
                drenator_id, drenator_end = values[i]
                if i == 0 and not force_pairs:
                    # run first drenator single if not force pairs
                    ids = [str(drenator_id)]
                    block = m.row('cleaning', push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator(ordered=False)),
                                  size=cast_t(cleaning_time),
                                  ids=ids,
                                  label=f'Дренатор {", ".join(ids)}{label_suffix}').block
                else:
                    if i + 1 < len(values) and (force_pairs or values[i + 1][1] <= block.y[0] + 2 and not is_tomorrow_day_off):
                        # run pair
                        ids = [str(drenator_id), str(values[i + 1][0])]
                        block = m.row('cleaning',
                                      push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator(ordered=False)),
                                      size=cast_t(cleaning_time),
                                      ids=ids,
                                      label=f'Дренатор {", ".join(ids)}{label_suffix}').block
                        i += 1
                    else:
                        # run single
                        ids = [str(drenator_id)]
                        block = m.row('cleaning', push_func=AxisPusher(start_from=drenator_end,
                                                                       validator=CleaningValidator(ordered=False)),
                                      size=cast_t(cleaning_time),
                                      ids=[drenator_id],
                                      label=f'Дренатор {", ".join(ids)}{label_suffix}').block
                i += 1

        with code('Main drenators'):
            # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
            values = properties['mozzarella'].drenator_times()
            for value in values:
                value[1] = cast_t(value[1])
                value[1] += 17 # add hour and 25 minutes of buffer
            values = list(sorted(values, key=lambda value: value[1]))

            _make_drenators(values, '01:20')
            used_ids = set([value[0] for value in values])

        with code('Non used drenators'):
            values = []
            # run drenators that are not present
            non_used_ids = set(range(1, 9)) - used_ids
            non_used_ids = [str(x) for x in non_used_ids]
            for non_used_id in non_used_ids:
                values.append([non_used_id, cast_t('10:00')])
            _make_drenators(values, '01:05', ' (кор. мойка)', force_pairs=True)

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:30'),
          label='Транспортер + линия кислой сыворотки')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:30'),
          label='Линия кислой сыворотки')

    return m.root


def make_contour_5(schedules, properties, input_tanks=(['4', 80], ['5', 80])):
    m = BlockMaker("5 contour")

    m.row('cleaning', push_func=add_push,
          size=cast_t('01:20'),
          label='Танк концентрата')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Танк концентрата')

    with code('scotta'):
        start_t = cast_t('06:30')
        for id, volume in input_tanks:
            if not volume:
                continue
            concentration_t = utils.custom_round(volume / 15 * 12, 1, 'ceil')
            start_t += concentration_t
            m.row('cleaning', push_func=AxisPusher(start_from=start_t, validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label=f'Танк рикотты')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия Ретентата')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия подачи на НФ открыть кран')

    m.row('cleaning', push_func=AxisPusher(start_from=cast_t('08:30'), validator=CleaningValidator(ordered=False)),
          size=cast_t('01:20'),
          label='Линия Концентрата на отгрузку')

    return m.root


def make_contour_6(schedules, properties):
    m = BlockMaker("6 contour")

    if 'milk_project' in schedules:
        m.row('cleaning', push_func=add_push,
              x=cast_t(properties['milk_project'].end_time),
              size=cast_t('01:20'),
              label='Линия сырого молока на роникс')

    with code('Танк рикотты 1 внутри дня'):
        whey_used = 1900 * properties['ricotta'].n_boilings
        if whey_used > 100000:
            m.row('cleaning', push_func=AxisPusher(start_from=cast_t('12:00'), validator=CleaningValidator(ordered=False)),
                  size=cast_t('01:20'),
                  label='Танк рикотты (сладкая сыворотка)')

    with code('cream tanks'):
        if 'mascarpone' in schedules:
            m.row('cleaning', push_func=AxisPusher(start_from=cast_t(properties['mascarpone'].fourth_boiling_group_adding_lactic_acid_time) + 12, validator=CleaningValidator(ordered=False)),
                                          size=cast_t('01:20'),
                                          label='Танк сливок') # fourth mascarpone boiling group end + hour

        m.row('cleaning', push_func=AxisPusher(start_from=cast_t('09:00'), validator=CleaningValidator(ordered=False)),
                                      size=cast_t('01:20'),
                                      label='Танк сливок')

    with code('mascarpone'):
        if 'mascarpone' in schedules:
            m.row('cleaning', push_func=AxisPusher(start_from=cast_t(properties['mascarpone'].last_pumping_off) + 6, validator=CleaningValidator(ordered=False)),
                  size=(cast_t('01:20'), 0),
                  label='Маскарпоне')

    ricotta_end = cast_t(properties['ricotta'].last_pumping_out_time) + 12
    m.row('cleaning', push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator(ordered=False)),
          size=cast_t('02:30'),
          label='Линия сладкой сыворотки')

    m.row('cleaning', push_func=AxisPusher(start_from=ricotta_end,
                                           validator=CleaningValidator(ordered=False)),
          size=cast_t('01:20'),
          label='Танк сливок')  # ricotta end + hour

    with code('Танк рикотты 1'):
        m.row('cleaning', push_func=AxisPusher(start_from=cast_t(properties['ricotta'].start_of_ninth_from_the_end_time), validator=CleaningValidator(ordered=False)),
              size=cast_t('01:20'),
              label='Танк рикотты (сладкая сыворотка)')

    for label in ['Линия сливок на подмес рикотта', 'Танк рикотты (скотта)', 'Танк рикотты (сладкая сыворотка)']:
        m.row('cleaning', push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator(ordered=False)),
              size=cast_t('01:20'),
              label=label)

    if 'butter' in schedules:
        m.row('cleaning', push_func=AxisPusher(start_from=cast_t(properties['butter'].end_time), validator=CleaningValidator(ordered=False)),
              size=cast_t('01:20'),
              label='Маслоцех')

    return m.root


def make_schedule(schedules, properties, **kwargs):
    m = BlockMaker("schedule")

    contours = [
        make_contour_1(schedules, properties, shipping_line=kwargs.get('shipping_line', True)),
        make_contour_2(schedules, properties),
        make_contour_3(schedules, properties, is_bar12_present=kwargs.get('is_bar12_present', False)),
        make_contour_4(schedules, properties, is_tomorrow_day_off=kwargs.get('is_tomorrow_day_off', False)),
        make_contour_5(schedules, properties, input_tanks=kwargs.get('input_tanks')),
        make_contour_6(schedules, properties),
    ]

    for contour in contours:
        m.col(contour, push_func=add_push)

    return m.root
