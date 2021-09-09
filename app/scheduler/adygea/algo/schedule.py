# fmt: off

from app.imports.runtime import *

from app.scheduler.adygea.algo.boilings import *
from app.scheduler.time import *
from app.models import *


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1['collecting'], b2['collecting'])
        if b1.props['boiler_num'] == b2.props['boiler_num']:
            validate_disjoint_by_axis(b1, b2)

    @staticmethod
    def validate__boiling__lunch(b1, b2):
        if b1.props['boiler_num'] >> 1 == b2.props['pair_num']: # 0, 1 -> 0, 2, 3 -> 1
            validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__boiling(b1, b2):
        if b2.props['boiler_num'] >> 1 == b1.props['pair_num']: # 0, 1 -> 0, 2, 3 -> 1
            validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__lunch(b1, b2):
        pass


def _make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00', lunch_times=None):
    lunch_times = lunch_times or []
    lunch_times = list(lunch_times)
    assert len(lunch_times) in [0, 2] # no lunches or two lunches for two teams

    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()
    adygea_line = cast_model(AdygeaLine, 7)
    adygea_cleaning = cast_model(Washer, 'adygea_cleaning')

    cur_boiler_num = 0
    cur_boiling_id = boiling_plan_df['boiling_id'].iloc[0] + first_boiling_id - 1
    for i, row in boiling_plan_df.iterrows():
        for _ in range(row['n_baths']):
            boiling = make_boiling(row['boiling'], boiling_id=cur_boiling_id, boiler_num=cur_boiler_num)
            push(m.root, boiling, push_func=AxisPusher(start_from='last_beg', start_shift=-30, min_start=0), validator=Validator())
            cur_boiler_num = (cur_boiler_num + 1) % 4

            with code('Push lunch if needed'):
                if lunch_times:
                    pair_num = cur_boiler_num % 2
                    if lunch_times[pair_num] and cast_time(boiling.y[0] + cast_t(start_time)) >= lunch_times[pair_num]:
                        push(m.root, make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num), push_func=AxisPusher(start_from=cast_t(lunch_times[pair_num]) - cast_t(start_time)), validator=Validator())
                        lunch_times[pair_num] = None # pushed lunch, nonify lunch time

            cur_boiling_id += 1

    with code('Push lunches if not pushed yet'):
        for pair_num, lunch_time in enumerate(lunch_times):
            if lunch_time:
                push(m.root, make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num), push_func=AxisPusher(start_from=cast_t(lunch_time) - cast_t(start_time)), validator=Validator())

    with code('Cleaning'):
        last_boilings = [utils.iter_get([boiling for boiling in m.root['boiling', True] if boiling.props['boiler_num'] == boiler_num], -1) for boiler_num in range(4)]
        last_boilings = [b for b in last_boilings if b]
        cleaning_start = min(b.y[0] for b in last_boilings)
        if len(m.root['lunch', True]) > 0:
            cleaning_start = max(cleaning_start, min(b.y[0] for b in m.root['lunch', True]))
        m.row(make_cleaning(size=adygea_cleaning.time // 5), x=cleaning_start, push_func=add_push)
    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root


def make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00'):
    no_lunch_schedule = _make_schedule(boiling_plan_df, first_boiling_id, start_time)
    if cast_time(no_lunch_schedule.y[0]) <= '00:12:30':
        lunch_times = []
    else:
        lunch_times = []
        for i, r in enumerate([range(0, 2), range(2, 4)]):
            range_boilings = [boiling for boiling in no_lunch_schedule['boiling', True] if boiling.props['boiler_num'] in r]

            # find lunch times
            for b1, b2, b3 in utils.iter_sequences(range_boilings, 3, method='any'):
                if not b2 and not b3:
                    # finished early
                    lunch_times.append('00:12:00')

                if not b2:
                    continue

                if cast_time(b2.y[0]) >= '00:12:00':
                    if b3 and b1:
                        if (b2.y[0] - b1.y[0]) >= (b3.y[0] - b2.y[0]):
                            # wait for next boiling and make lunch
                            lunch_times.append(cast_time(b3.y[0]))
                        else:
                            # make lunch now
                            lunch_times.append(cast_time(b2.y[0]))
                    else:
                        # make lunch now
                        lunch_times.append(cast_time(b2.y[0]))
                    break


    return _make_schedule(boiling_plan_df, first_boiling_id, start_time, lunch_times=lunch_times)
