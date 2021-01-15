from utils_ak.block_tree import *
from app.schedule_maker.algo.cooling import make_cooling_process
from app.schedule_maker.algo.boiling import make_boiling
from app.schedule_maker.calculation import *


class boilings_dataframes_to_boilings:
    def _make_line(self, df, line_name, item_name):
        if len(df) == 0:
            raise Exception('Should not happen')
        start_from = df.iloc[0]['beg']

        maker, make = init_block_maker(line_name, x=(start_from // 5, 0))

        for i, row in df.iterrows():
            make(row['name'], size=((row['end'] - row['beg']) // 5, 0), x=(row['beg'] // 5 - start_from // 5, 0), push_func=add_push, **{item_name: row['item']})
        return maker.root

    def _make_cooling_line(self, df, boiling_model):
        assert len(df) > 0, 'Should not happen'

        start_from = df.iloc[0]['beg']
        maker, make = init_block_maker('coolings', x=(start_from // 5, 0))

        for i, row in df.iterrows():
            cooling_process = make_cooling_process(boiling_model=boiling_model, cooling_technology=row['item'].default_cooling_technology, bff=row['item'], size=(row['end'] - row['beg']) // 5, x=(row['beg'] // 5 - start_from // 5, 0))
            make(cooling_process, push_func=add_push, bff=row['item'])
        return maker.root

    def _make_melting_and_packing(self, boiling_dataframes, boiling_model):
        maker, make = init_block_maker('melting_and_packing')

        with make('melting'):
            serving = make('serving', size=(boiling_model.line.serving_time // 5, 0), push_func=add_push).block

            line = self._make_line(boiling_dataframes['meltings'], 'meltings', 'bff')
            line.props.update({'x': (serving.size[0], 0)})
            push(maker.root['melting'], line, push_func=add_push)

            line = self._make_cooling_line(boiling_dataframes['coolings'], boiling_model)
            line.props.update({'x': (serving.size[0], 0)})
            push(maker.root['melting'], line, push_func=add_push)

        for packing_team_id, df in boiling_dataframes['packings'].items():
            line = self._make_line(df, 'packing',  'sku')
            line.props.update({'x': (serving.size[0] + line.x[0], 0), 'packing_team_id': int(packing_team_id)})
            push(maker.root, line, push_func=add_push)
        return maker.root

    def __call__(self, boilings_dataframes, boiling_model, start_from_id):
        res = []
        for i, boiling_dataframes in enumerate(boilings_dataframes):
            mp = self._make_melting_and_packing(boiling_dataframes, boiling_model)
            boiling = make_boiling(boiling_model, start_from_id + i, mp)
            res.append(boiling)
        return res
