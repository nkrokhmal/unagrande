from utils_ak.block_tree import BlockMaker

from app.enum import LineName


def make_cooling_process(line_name, cooling_technology, melting_process_size=None, size=None, *args, **kwargs):
    m = BlockMaker("cooling_process", *args, **kwargs)
    with m.block("start"):
        cooling_times = (
            [
                cooling_technology.first_cooling_time,
                cooling_technology.second_cooling_time,
            ]
            if line_name == LineName.WATER
            else [cooling_technology.salting_time]
        )
        for cooling_time in cooling_times:
            m.row("cooling", size=cooling_time // 5)

    if size:
        melting_process_size = size - m.root["start"].size[0]

    with m.block("finish"):
        m.row("cooling", size=melting_process_size)
    return m.root
