import anyconfig
from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.schedule_maker.utils import *
from app.schedule_maker.validation import *
from app.schedule_maker.blocks import *
from app.schedule_maker.style import *
from itertools import product

from collections import OrderedDict


def gen_request_df(request):
    values = []
    for boiling in request['Boilings']:
        for sku_id, sku_kg in boiling['SKUVolumes'].items():
            values.append([boiling['BoilingId'], sku_id, sku_kg])
    df = pd.DataFrame(values)

    values = []
    for boiling_id, boiling_grp in df.groupby(0):
        boiling_dic = boiling_grp[[1, 2]].set_index(1).to_dict(orient='index')
        boiling_dic = {k: v[2] for k, v in boiling_dic.items()}  # {'34': 1110.0, '35': 0.0, ...}
        boiling_dic = {cast_sku(k): v for k, v in boiling_dic.items()} # {<SKU 34>: 1110.0, ...}
        total_kg = sum(boiling_dic.values())

        # round to get full
        # todo: proper logic
        total_kg = custom_round(total_kg, 850, rounding='floor')

        n_boilings = int(total_kg / 850)
        for i in range(n_boilings):
            cur_kg = 850

            boiling_request = OrderedDict()
            for k, v in list(boiling_dic.items()):
                boil_kg = min(cur_kg, boiling_dic[k])

                boiling_dic[k] -= boil_kg
                cur_kg -= boil_kg

                if k not in boiling_request:
                    boiling_request[k] = 0
                boiling_request[k] += boil_kg

                if cur_kg == 0:
                    break

            if cur_kg != 0:
                # any non-zero
                print('Non-zero')
                k = [k for k, v in boiling_request.items() if v != 0][0]
                boiling_request[k] += cur_kg

            boiling_request = {k: v for k, v in boiling_request.items() if v != 0}
            values.append([boiling_id, boiling_request])
    df = pd.DataFrame(values, columns=['boiling_id', 'boiling_request'])
    df['boiling_id'] = df['boiling_id'].astype(str)
    df['boiling_type'] = df['boiling_id'].apply(lambda boiling_id: 'salt' if str(cast_boiling(boiling_id).percent) == '2.7' else 'water')
    df['used'] = False

    return df


def pick(df, boiling_type):
    tmp = df
    tmp = tmp[tmp['used'] == False]
    tmp = tmp[tmp['boiling_type'] == boiling_type]

    if len(tmp) == 0:
        return

    row = tmp.iloc[0]
    df.loc[row.name, 'used'] = True
    return row


def make_schedule(request, date):
    df = gen_request_df(request)

    # draw salt and water
    root = Block('root')

    def make_boiling_row(i, row, last_packing_sku):
        return make_boiling(cast_boiling(row['boiling_id']), row['boiling_request'], row['boiling_type'], block_num=i + 1, last_packing_sku=last_packing_sku)

    iter_water_props = [{'pouring_line': str(v)} for v in [0, 1]]
    iter_salt_props_2 = [{'pouring_line': str(v[0]), 'melting_line': str(v[1])} for v in product([2, 3], [0, 1, 2, 3])]
    # [lines.extra_salt_cheesemaker]
    iter_salt_props_3 = [{'pouring_line': str(v[0]), 'melting_line': str(v[1])} for v in product([1, 2, 3], [0, 1, 2, 3])]
    iter_salt_props = iter_salt_props_2

    last_packing_skus = {} # {boiling_type: last_packing_sku}

    # will be initialized one of the two first blocks
    last_cleaning_t = None

    latest_boiling = None

    # [cheesemakers.start_time]
    water_start_time = '09:50'
    salt_start_time = '07:05'

    i, row = 0, pick(df, 'water')
    if row is not None:
        # there is water boiling today
        b = make_boiling_row(i, row, None)
        beg = cast_t(water_start_time) - b['melting_and_packing'].beg
        boiling = dummy_push(root, b, iter_props=iter_water_props, validator=boiling_validator, beg=beg, max_tries=100)
        last_packing_skus[row['boiling_type']] = list(row['boiling_request'].keys())[-1]

        # init last cleaning with termizator first start
        last_cleaning_t = last_cleaning_t if last_cleaning_t else beg
        latest_boiling = boiling if not latest_boiling else max([latest_boiling, boiling], key=lambda boiling: boiling.beg)
    latest_water_boiling = boiling

    i, row = 1, pick(df, 'salt')
    if row is not None:
        # there is a salt boiling today
        b = make_boiling_row(i, row, None)
        beg = cast_t(salt_start_time) - b['melting_and_packing'].beg
        boiling = dummy_push(root, b, iter_props=iter_salt_props, validator=boiling_validator, beg=beg, max_tries=100)
        last_packing_skus[row['boiling_type']] = list(row['boiling_request'].keys())[-1]

        # init last cleaning with termizator first start
        last_cleaning_t = last_cleaning_t if last_cleaning_t else beg
        latest_boiling = boiling if not latest_boiling else max([latest_boiling, boiling], key=lambda boiling: boiling.beg)
    latest_salt_boiling = boiling

    cur_i = 2

    while True:
        left_df = df[~df['used']]
        left_unique = left_df['boiling_type'].unique()

        if len(left_unique) == 1:
            boiling_type = left_unique[0]

            if boiling_type == 'salt':
                # start working for 3 lines on salt
                # [lines.extra_salt_cheesemaker]
                iter_salt_props = iter_salt_props_3
        elif len(left_unique) == 0:
            # stop production
            break
        else:
            # make different block
            boiling_type = 'water' if latest_boiling.props['boiling_type'] == 'salt' else 'salt'

        row = pick(df, boiling_type)

        beg = latest_water_boiling.beg if boiling_type == 'water' else latest_salt_boiling.beg

        print('Starting from', beg, boiling_type, latest_water_boiling.beg, latest_salt_boiling.beg)

        b = make_boiling_row(cur_i, row, last_packing_skus[row['boiling_type']])
        iter_props = iter_water_props if boiling_type == 'water' else iter_salt_props
        boiling = dummy_push(root, b, iter_props=iter_props, validator=boiling_validator, beg=int(beg), max_tries=100)
        last_packing_skus[row['boiling_type']] = list(row['boiling_request'].keys())[-1]
        latest_boiling = boiling if not latest_boiling else max([latest_boiling, boiling], key=lambda boiling: boiling.beg)

        if boiling_type == 'water':
            latest_water_boiling = boiling
        else:
            latest_salt_boiling = boiling

        cur_i += 1

        # [termizator.cleaning]
        # add cleaning if necessary
        boilings = [node for node in root.children if node.props['class'] == 'boiling']
        a, b = list(boilings[-2:])

        rest = b['pouring'][0]['termizator'].beg - a['pouring'][0]['termizator'].end
        if 12 <= rest < 18:
            # [termizator.cleaning.1]
            cleaning = make_termizator_cleaning_block('short')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].beg - cleaning.size})
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end
        elif rest >= 18:
            # [termizator.cleaning.2]
            cleaning = make_termizator_cleaning_block('full')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].beg - cleaning.size})
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end

        # add cleaning if working more than 12 hours without cleaning
        if b['pouring'][0]['termizator'].end - last_cleaning_t > cast_t('12:00'):
            # [termizator.cleaning.3]
            cleaning = make_termizator_cleaning_block('short')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].end})

            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end + cleaning.size

    # add final cleaning [termizator.cleaning.4]
    cleaning = make_termizator_cleaning_block('full')
    boilings = [node for node in root.children if node.props['class'] == 'boiling']

    cleaning.props.update({'t': boilings[-1]['pouring'][0]['termizator'].end + 1}) # add five minutes extra
    add_push(root, cleaning)

    root.props.update({'size': max(c.end for c in root.children)}, accumulate=['size', 'time_size'])
    return root


# todo: better naming
def draw_workbook(root, mode='prod', template_fn=None):
    style = load_style(mode=mode)
    root.props.update({'size': max(c.end for c in root.children)}, accumulate=['size', 'time_size'])
    init_sheet_func = init_sheet if mode == 'dev' else init_template_sheet(template_fn=template_fn)
    return draw_schedule(root, style, init_sheet_func=init_sheet_func)
