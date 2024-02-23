from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.builtin.collection import delistify
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.numeric import custom_round

from app.globals import db
from app.models import BrynzaBoiling, BrynzaSKU


def make_brynza_boiling(boiling_id: int):
    # - Init block maker

    m = BlockMaker("root")

    # - Get models

    skus = [sku for sku in db.session.query(BrynzaSKU).all() if sku.group.name == "Брынза"]

    if not skus:
        raise Exception("No brynza skus found")

    sku = skus[0]

    boilings = [bm for bm in db.session.query(BrynzaBoiling).all() if sku in bm.skus]

    if not boilings:
        raise Exception("No brynza boiling models found")

    boiling = boilings[0]

    boiling_technology = boiling.boiling_technologies[0]

    # - Make brynza boiling
    with m.block(
        "boiling",
        boiling_id=boiling_id,
    ):
        m.row("pouring", size=boiling_technology.pouring_time // 5)
        m.row("soldification", size=boiling_technology.soldification_time // 5)
        m.row("cutting", size=boiling_technology.cutting_time // 5)
        m.row("pouring_off", size=boiling_technology.pouring_off_time // 5)
        m.row("extra", size=2)

    return m.root["boiling"]


def test():
    print(make_brynza_boiling(1))


if __name__ == "__main__":
    test()
