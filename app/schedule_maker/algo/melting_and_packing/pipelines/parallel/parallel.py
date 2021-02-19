from utils_ak.interactive_imports import *
from app.schedule_maker.models import *

from app.schedule_maker.algo import make_boiling
from app.schedule_maker.algo.packing import *
from app.schedule_maker.algo.cooling import *
from app.schedule_maker.calculation import *
from app.schedule_maker.algo.melting_and_packing.melting_process import make_melting_and_packing_from_mpps


def make_mpp(boiling_df, left_boiling_volume):
    boiling_df['collecting_speed'] = boiling_df['sku'].apply(lambda sku: sku.collecting_speed)
    boiling_df['packing_speed'] = boiling_df['sku'].apply(lambda sku: sku.packing_speed)
    boiling_df['cur_speed'] = 0
    boiling_df['collected'] = 0
    boiling_df['beg_ts'] = None
    boiling_df['end_ts'] = None

    boiling_model = boiling_df.iloc[0]['boiling']
    boiling_volume = min(boiling_df['left'].sum(), left_boiling_volume)
    packing_team_ids = remove_duplicates(boiling_df['packing_team_id'])

    old_ts = 0
    cur_ts = 0

    left = boiling_volume

    assert left < boiling_df['left'].sum() + ERROR  # have enough packers to collect |this volume

    while left > ERROR:
        # get next skus
        cur_skus_values = []
        for packing_team_id in packing_team_ids:
            team_df = boiling_df[(boiling_df['packing_team_id'] == packing_team_id) & (boiling_df['left'] > ERROR)]
            if len(team_df) > 0:
                cur_skus_values.append(team_df.iloc[0])
        cur_skus_df = pd.DataFrame(cur_skus_values).sort_values(by=['collecting_speed', 'packing_team_id'])  # two rows for next packing skus

        collecting_speed_left = boiling_model.line.melting_speed
        for i, cur_sku in cur_skus_df.iterrows():
            cur_speed = min(collecting_speed_left, cur_sku['collecting_speed'])
            if not cur_speed:
                continue
            boiling_df.at[cur_sku.name, 'cur_speed'] = cur_speed
            collecting_speed_left -= cur_speed

            # set start of packing
            if cur_sku['beg_ts'] is None:
                boiling_df.at[cur_sku.name, 'beg_ts'] = cur_ts

        df = boiling_df[boiling_df['cur_speed'] > 0]

        old_ts = cur_ts
        cur_ts = old_ts + min((df['left'] / df['cur_speed']).min(), left / df['cur_speed'].sum()) * 60  # either one of the skus are collected or the boiling is over

        # update collected kgs
        boiling_df['left'] -= (cur_ts - old_ts) * boiling_df['cur_speed'] / 60
        boiling_df['collected'] += (cur_ts - old_ts) * boiling_df['cur_speed'] / 60
        left -= (cur_ts - old_ts) * boiling_df['cur_speed'].sum() / 60
        boiling_df['cur_speed'] = 0

        boiling_df['end_ts'] = np.where((~boiling_df['beg_ts'].isnull()) & boiling_df['end_ts'].isnull() & (boiling_df['left'] < ERROR), cur_ts, boiling_df['end_ts'])

        assert boiling_df['left'].min() >= -ERROR  # check that all quantities are positive

    # set current time - collected how much we could
    boiling_df['end_ts'] = np.where((~boiling_df['beg_ts'].isnull()) & boiling_df['end_ts'].isnull(), cur_ts, boiling_df['end_ts'])

    def round_timestamps(df, packing_team_ids):
        # round to five-minute intervals
        df['beg_ts'] = df['beg_ts'].apply(lambda ts: None if ts is None else custom_round(ts, 5, 'nearest_half_down'))
        df['end_ts'] = df['end_ts'].apply(lambda ts: None if ts is None else custom_round(ts, 5, 'nearest_half_down'))

        # fix small intervals (like beg_ts and end_ts: 5, 5 -> 5, 10)
        for packing_team_id in packing_team_ids:
            grp = df[boiling_df['packing_team_id'] == packing_team_id]
            grp = grp[~grp['beg_ts'].isnull()]
            cur_fix = 0
            for i, row in grp.iterrows():
                df.at[i, 'beg_ts'] += cur_fix
                if row['beg_ts'] == row['end_ts']:
                    cur_fix += 5
                df.at[i, 'end_ts'] += cur_fix
    round_timestamps(boiling_df, packing_team_ids)

    # create block
    maker, make = init_block_maker('melting_and_packing_process', axis=1)

    # create packing blocks
    last_collecting_process_y = 0 # todo: redundant?
    for packing_team_id in packing_team_ids:
        df = boiling_df[boiling_df['packing_team_id'] == packing_team_id]
        df = df[~df['beg_ts'].isnull()]
        if len(df) > 0:
            packing = make('packing', packing_team_id=packing_team_id, x=(df.iloc[0]['beg_ts'] // 5, 0), push_func=add_push).block

            with make('collecting', packing_team_id=packing_team_id, x=(df.iloc[0]['beg_ts'] // 5, 0), push_func=add_push):
                for i, (_, row) in enumerate(df.iterrows()):
                    if row['collecting_speed'] == row['packing_speed']:
                        # add configuration if needed
                        if i >= 1:
                            conf_time_size = get_configuration_time(boiling_model.line.name, row['sku'], df.iloc[i - 1]['sku'])
                            if conf_time_size:
                                block = make('packing_configuration', size=[conf_time_size // 5, 0]).block
                                push(packing, maker.copy(block), push_func=add_push)
                        block = make('process', size=(custom_round(row['end_ts'] - row['beg_ts'], 5, 'ceil') // 5, 0), sku=row['sku']).block
                        last_collecting_process_y = max(last_collecting_process_y, block.y[0])
                        push(packing, maker.create_block('process', size=block.props['size'], x=list(block.props['x_rel']), sku=row['sku']), push_func=add_push)
                    else:
                        # rubber
                        block = make('process', size=(custom_round(row['end_ts'] - row['beg_ts'], 5, 'ceil') // 5, 0), sku=row['sku']).block
                        last_collecting_process_y = max(last_collecting_process_y, block.y[0])
                        packing_size = custom_round(row['collected'] / row['packing_speed'] * 60, 5, 'ceil') // 5
                        push(packing, maker.create_block('process', size=[packing_size, 0], x=list(block.props['x_rel']), sku=row['sku']), push_func=add_push)

    bff = boiling_df.iloc[0]['bff']

    make('melting_process', size=(last_collecting_process_y, 0), bff=bff)

    make(make_cooling_process(boiling_model.line.name, bff.default_cooling_technology, last_collecting_process_y))

    # shift packing and collecting for cooling
    for packing in listify(maker.root['packing']):
        packing.props.update(x=[packing.props['x'][0] + maker.root['cooling_process']['start'].y[0], 0])
    for collecting in listify(maker.root['collecting']):
        collecting.props.update(x=[collecting.props['x'][0] + maker.root['cooling_process']['start'].y[0], 0])

    maker.root.props.update(kg=boiling_volume)

    return maker.root


def make_boilings_parallel_dynamic(boiling_group_df):
    boilings = []

    boiling_group_df = boiling_group_df.copy()

    boiling_model = boiling_group_df.iloc[0]['boiling']
    boiling_volumes = boiling_group_df.iloc[0]['boiling_volumes']
    values = []
    for _, grp in boiling_group_df.groupby(['packing_team_id', 'sku_name']):
        value = grp.iloc[0]
        value['kg'] = grp['kg'].sum()
        values.append(value)

    grouped_df = pd.DataFrame(values)

    def get_original_index(sku):
        for i, row in boiling_group_df.iterrows():
            if row['sku'] == sku:
                return i
        raise Exception('Sould not happen. Did not find sku in original boiling_group_id.')

    grouped_df['original_index'] = grouped_df['sku'].apply(get_original_index)
    grouped_df = grouped_df.sort_values('original_index')
    grouped_df.pop('original_index')

    grouped_df['left'] = grouped_df['kg']

    group_id = grouped_df.iloc[0]['group_id']
    form_factors = remove_duplicates(grouped_df['bff'])

    cur_form_factor = form_factors[0]
    cur_boiling_df = grouped_df[grouped_df['bff'] == cur_form_factor]

    for i, boiling_volume in enumerate(boiling_volumes):
        mpps = []

        left = boiling_volume

        while left > ERROR:
            # get next cur_boiling_df if necessary
            if cur_boiling_df['left'].sum() < ERROR:
                assert form_factors.index(cur_form_factor) + 1 < len(form_factors)  # check there are form factors left
                cur_form_factor = form_factors[form_factors.index(cur_form_factor) + 1]
                cur_boiling_df = grouped_df[grouped_df['bff'] == cur_form_factor]
            mpp = make_mpp(cur_boiling_df, left)
            mpps.append(mpp)
            left -= mpp.props['kg']

        melting_and_packing = make_melting_and_packing_from_mpps(boiling_model, mpps)
        boiling = make_boiling(boiling_model, group_id + i, boiling_volume, melting_and_packing)
        boilings.append(boiling)

    return boilings
