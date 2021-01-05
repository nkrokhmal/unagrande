from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.schedule_maker.blocks.packing import *


def make_melting_and_packing_basic(boiling_plan):
    boiling_model = boiling_plan.iloc[0]['boiling']

    boiling_plan = boiling_plan.copy()
    # todo: make properly
    boiling_plan['bff'] = boiling_plan['sku'].apply(lambda sku: sku.boiling_form_factors[0])
    mark_consecutive_groups(boiling_plan, 'bff', 'bff_group')

    maker, make = init_block_maker('melting_and_packing')

    with make('melting'):
        serving = make('serving', size=(boiling_model.meltings.serving_time // 5, 0), push_func=add_push).block
        meltings = make('meltings', x=(serving.size[0], 0), push_func=add_push).block
        coolings = make('coolings', x=(serving.size[0], 0), push_func=add_push).block

        for i, (group, grp) in enumerate(boiling_plan.groupby('bff_group')):
            if i >= 1 and boiling_model.boiling_type == 'water':
                # non-first group - reconfigure time
                push(meltings, maker.create_block('melting_configuration', size=(1, 0)))

            melting_process = maker.create_block('melting_process',
                                                 size=(custom_round(grp['kg'].sum() / boiling_model.meltings.speed * 60, 5, 'ceil') // 5, 0),
                                                 bff=grp.iloc[0]['bff'])

            push(meltings, melting_process)

            # add cooling
            cooling_process = maker.create_block('cooling_process', x=melting_process.props['x_rel'])
            _, cooling_make = init_block_maker(cooling_process)

            with cooling_make('start'):
                if boiling_model.boiling_type == 'water':
                    cooling_make('cooling', size=(boiling_model.meltings.first_cooling_time // 5, 0))
                    cooling_make('cooling', size=(boiling_model.meltings.second_cooling_time // 5, 0))
                elif boiling_model.boiling_type == 'salt':
                    cooling_make('salting', size=(boiling_model.meltings.salting_time // 5, 0))

            with cooling_make('finish'):
                if boiling_model.boiling_type == 'water':
                    cooling_make('cooling', size=(melting_process.size[0], 0))
                elif boiling_model.boiling_type == 'salt':
                    cooling_make('salting', size=(melting_process.size[0], 0))

            push(coolings, cooling_process, push_func=add_push)

    with make('packing',
              x=(listify(maker.root['melting']['coolings']['cooling_process'])[0]['start'].y[0], 0),
              packing_team_id=1, push_func=add_push):
        for i, (_, row) in enumerate(boiling_plan.iterrows()):
            sku, kg = row['sku'], row['kg']
            packing_speed = min(sku.packing_speed, boiling_model.meltings.speed)
            make('packing_process',
                 size=[custom_round(kg / packing_speed * 60, 5, rounding='ceil') // 5, 0],
                 sku=sku)

            if i != len(boiling_plan) - 1:
                # add configuration
                conf_time_size = get_configuration_time(boiling_model, sku, boiling_plan.iloc[i + 1]['sku'])

                if conf_time_size:
                    make('packing_configuration', size=[conf_time_size // 5, 0])

    return maker.root