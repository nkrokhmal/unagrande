import os
os.environ['environment'] = 'interactive'

from app.schedule_maker.boiling_plan import *


def test_read_boiling_plan():
    print(read_boiling_plan_new('data/sample_boiling_plan_new.xlsx'))


if __name__ == '__main__':
    test_read_boiling_plan()