# fmt: off

from app.imports.runtime import *

from app.scheduler.adygea.algo.boilings import *
from app.scheduler.adygea.algo.cleanings import *
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


def make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00'):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()

    cur_boiler_num = 0
    cur_boiling_id = boiling_plan_df['boiling_id'].iloc[0] + first_boiling_id - 1
    for i, row in boiling_plan_df.iterrows():
        for _ in range(row['n_baths']):
            boiling = make_boiling(row['boiling'], boiling_id=cur_boiling_id, boiler_num=cur_boiler_num)
            push(m.root, boiling, push_func=AxisPusher(start_from='last_beg'), validator=Validator())
            cur_boiler_num = (cur_boiler_num + 1) % 4
            cur_boiling_id += 1

    for i, r in enumerate([range(0, 2), range(2, 4)]):
        end = max(boiling.y[0] for boiling in m.root['boiling', True] if boiling.props['boiler_num'] in r)
        m.row(make_cleaning(pair_num=i), x=end + 1, push_func=add_push)

    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root
