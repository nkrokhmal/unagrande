from utils_ak.interactive_imports import *

from app.schedule_maker.algo.boiling import make_boiling
from app.schedule_maker.algo.melting_and_packing import *

from app.enum import LineName


def make_boilings_basic(boiling_plan_df):
    boiling_plan_df = boiling_plan_df.copy()

    boilings = []

    for boiling_id, boiling_plan in boiling_plan_df.groupby('batch_id'):
        boiling_model = boiling_plan.iloc[0]['boiling']
        melting_and_packing = make_melting_and_packing_basic(boiling_plan)
        boiling = make_boiling(boiling_model, boiling_id, melting_and_packing)
        boilings.append(boiling)
    return boilings


def make_boilings_by_groups(boiling_plan_df):
    boiling_plan_df = boiling_plan_df.copy()
    boiling_plan_df['is_lactose'] = boiling_plan_df['boiling'].apply(lambda boiling: boiling.is_lactose)

    for _, boiling_plan in boiling_plan_df.groupby('batch_id'):
        # todo: hardcode
        if len(boiling_plan['boiling'].unique()) > 1:
            if len(boiling_plan['is_lactose'].unique()) == 1:
                raise Exception('Only one boiling model allowed in boiling plan')
            if len(boiling_plan[~boiling_plan['is_lactose']]) == 0:
                raise Exception('Only if lactose is present boiling model can be changed')

            boiling_plan_df.at[boiling_plan.index, 'boiling'] = boiling_plan[~boiling_plan['is_lactose']].iloc[0]['boiling']

    mark_consecutive_groups(boiling_plan_df, 'boiling', 'boiling_group')

    res = []
    for boiling_group, grp in boiling_plan_df.groupby('boiling_group'):
        if grp.iloc[0]['boiling'].line.name == LineName.WATER:
            res += make_flow_water_boilings(grp, start_from_id=len(res) + 1)
            # res += make_boilings_basic(grp)
        else:
            # res += make_boilings_basic(grp)
            res += make_boilings_parallel_dynamic(grp)
    return res
