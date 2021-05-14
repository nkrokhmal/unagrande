from app.imports.runtime import *

from app.scheduler.mozarella.algo.cooling import make_cooling_process
from app.scheduler.mozarella.algo.boiling import make_boiling
from app.scheduler.calculation import *


class BoilingsDataframesToBoilings:
    def _make_line(self, df, line_name, item_name):
        if len(df) == 0:
            raise Exception("Should not happen")
        start_from = df.iloc[0]["beg"]

        maker, make = utils.init_block_maker(line_name, x=(start_from // 5, 0))

        for i, row in df.iterrows():
            make(
                row["name"],
                size=((row["end"] - row["beg"]) // 5, 0),
                x=(row["beg"] // 5 - start_from // 5, 0),
                push_func=utils.add_push,
                **{item_name: row["item"]}
            )
        return maker.root

    def _make_cooling_line(self, df, boiling_model):
        assert len(df) > 0, "Should not happen"

        start_from = df.iloc[0]["beg"]
        maker, make = utils.init_block_maker("coolings", x=(start_from // 5, 0))

        for i, row in df.iterrows():
            cooling_process = make_cooling_process(
                boiling_model.line.name,
                cooling_technology=row["item"].default_cooling_technology,
                bff=row["item"],
                size=(row["end"] - row["beg"]) // 5,
                x=(row["beg"] // 5 - start_from // 5, 0),
            )
            make(cooling_process, push_func=utils.add_push, bff=row["item"])
        return maker.root

    def _make_melting_and_packing(self, boiling_dataframes, boiling_model):
        maker, make = utils.init_block_maker("melting_and_packing")

        with make("melting"):
            serving = make(
                "serving",
                size=(boiling_model.line.serving_time // 5, 0),
                push_func=utils.add_push,
            ).block

            line = self._make_line(boiling_dataframes["meltings"], "meltings", "bff")
            line.props.update(x=(serving.size[0], 0))
            utils.push(maker.root["melting"], line, push_func=utils.add_push)

            line = self._make_cooling_line(
                boiling_dataframes["coolings"], boiling_model
            )
            line.props.update(x=(serving.size[0], 0))
            utils.push(maker.root["melting"], line, push_func=utils.add_push)

        # NOTE: collecting processes are the same with packing processes on water before rounding, but may differ after rounding
        for packing_team_id, df in boiling_dataframes["collectings"].items():
            line = self._make_line(df, "collecting", "sku")
            line.props.update(
                x=(serving.size[0] + line.x[0], 0), packing_team_id=int(packing_team_id)
            )
            utils.push(maker.root, line, push_func=utils.add_push)

        for packing_team_id, df in boiling_dataframes["packings"].items():
            line = self._make_line(df, "packing", "sku")
            line.props.update(
                x=(serving.size[0] + line.x[0], 0), packing_team_id=int(packing_team_id)
            )
            utils.push(maker.root, line, push_func=utils.add_push)
        return maker.root

    def __call__(
        self, boiling_volumes, boilings_dataframes, boiling_model, start_from_id
    ):
        res = []
        for i in range(len(boiling_volumes)):
            mp = self._make_melting_and_packing(boilings_dataframes[i], boiling_model)
            boiling = make_boiling(
                boiling_model, start_from_id + i, boiling_volumes[i], mp
            )
            res.append(boiling)
        return res