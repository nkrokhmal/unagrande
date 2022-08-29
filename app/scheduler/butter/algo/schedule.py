# fmt: off

from app.imports.runtime import *
from app.models import *
from app.scheduler.butter.algo.boilings import *
from app.scheduler.time import *


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=20)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__displacement(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1['pasteurization'], b2['pasteurization'], ordered=True)

    @staticmethod
    def validate__displacement__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__packing(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__packing__packing(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True, distance=4)

    @staticmethod
    def validate__packing__displacement(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__packing__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)


def make_schedule(boiling_plan_df, start_time='07:00'):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()

    sample_row = boiling_plan_df.iloc[0]
    line = sample_row['boiling'].line

    m.row('preparation', size=line.preparing_time // 5)

    for boiling_id, grp in boiling_plan_df.groupby("boiling_id"):
        boiling, packing = make_boiling_and_packing(grp)
        m.block(boiling,
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={'validator': Validator()})
        m.block(packing,
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={'validator': Validator()})
    m.block(m.create_block('displacement', size=(line.displacement_time // 5, 1)),
                 push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                 push_kwargs={'validator': Validator()})

    m.block(m.create_block('cleaning',  size=(line.cleaning_time // 5, 1)),
                 push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                 push_kwargs={'validator': Validator()})

    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root
