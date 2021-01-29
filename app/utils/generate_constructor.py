from app.interactive_imports import *
import pandas as pd
import numpy as np
from flask import current_app
import math
from copy import deepcopy


def generate_constructor_df_v3(df_copy):
    df = df_copy.copy()
    df['plan'] = df['plan'].apply(lambda x: round(x))
    df['boiling_type'] = df['boiling_id'].apply(lambda boiling_id: cast_boiling(boiling_id).boiling_type)
    df['weight'] = df['sku'].apply(lambda x:
                                   x.form_factor.relative_weight + 30 if 'Терка' in x.form_factor.name else
                                   x.form_factor.relative_weight)
    df['percent'] = df['sku'].apply(lambda x: x.made_from_boilings[0].percent)
    df['is_lactose'] = df['sku'].apply(lambda x: x.made_from_boilings[0].is_lactose)
    df['ferment'] = df['sku'].apply(lambda x: x.made_from_boilings[0].ferment)
    df['pack_weight'] = df['sku'].apply(lambda x: x.weight_netto)
    df['group'] = df['sku'].apply(lambda x: x.group.name)

    water, boiling_number = handle_water(df[df['boiling_type'] == 'water'])
    salt, boiling_number = handle_salt(df[df['boiling_type'] == 'salt'], boiling_number=boiling_number + 1)
    result = pd.concat([water, salt])
    result['kg'] = result['plan']
    result['boiling'] = result['boiling_id'].apply(lambda x: cast_boiling(x))
    result['name'] = result['sku'].apply(lambda sku: sku.name)
    result['boiling_name'] = result['boiling'].apply(lambda b: b.to_str())
    result['boiling_volume'] = np.where(result['boiling_type'] == 'salt', 850, 1000)
    result['packer'] = result['sku'].apply(lambda sku: sku.packers_str)
    result['form_factor'] = result['sku'].apply(lambda sku: sku.form_factor.weight_with_line)
    result['boiling_form_factor'] = result['sku'].apply(lambda sku: get_boiling_form_factor(sku))

    result = result[
        ['id', 'boiling_id', 'boiling_name', 'boiling_volume', 'group', 'form_factor', 'boiling_form_factor', 'packer',
         'name', 'kg', 'tag']]
    return result


def handle_water(df, max_weight=1000, min_weight=1000, boiling_number=1):
    boilings = Boilings(max_weight=max_weight, min_weight=min_weight, boiling_number=boiling_number)
    orders = [
        # (False, 3.3, 'Альче', None),
        # (True, 3.3, 'Альче', 'Фиор Ди Латте'),
        (None, 3.3, 'Альче', None),
        (True, 3.3, 'Сакко', 'Фиор Ди Латте'),
        (True, 3.6, 'Альче', 'Фиор Ди Латте'),
        (True, 3.6, 'Альче', 'Чильеджина'),
        (True, 3.3, 'Альче', 'Чильеджина'),
        (True, 3.3, 'Сакко', 'Чильеджина')]

    for order in orders:
        df_filter = df[(order[0] is None or df['is_lactose'] == order[0]) &
                       (df['percent'] == order[1]) &
                       (df['ferment'] == order[2]) &
                       (order[3] is None or df['group'] == order[3])]

        if not order[0]:
            df_filter_chl = df_filter[
                (df_filter['group'] == 'Чильеджина') &
                (~df_filter['is_lactose'])]\
                    .sort_values(by='weight', ascending=False)

            df_filter_fdl = df_filter[
                (df_filter['group'] == 'Фиор Ди Латте') &
                (~df_filter['is_lactose'])].sort_values(by='weight', ascending=False)

            df_filter_oth = df_filter[
                df_filter['is_lactose']].sort_values(by='weight', ascending=False)

            total_sum_without_lactose = df_filter[(~df_filter['is_lactose'])]['plan'].sum()
            total_sum = df_filter['plan'].sum()

            if total_sum // max_weight == total_sum_without_lactose // max_weight:
                if (df_filter_chl['plan'].sum() < 100) and (df_filter_oth['plan'].sum() < 100):
                    order = [df_filter_chl, df_filter_oth, df_filter_fdl]
                elif (df_filter_chl['plan'].sum() < 100) and (df_filter_oth['plan'].sum() > 100):
                    order = [df_filter_chl, df_filter_fdl, df_filter_oth]
                elif (df_filter_chl['plan'].sum() > 100) and (df_filter_oth['plan'].sum() < 100):
                    order = [df_filter_oth, df_filter_fdl, df_filter_chl]
                else:
                    order = [df_filter_fdl, df_filter_chl, df_filter_oth]
                df_filter_dict = pd.concat(order).to_dict('records')
                boilings.add_group(df_filter_dict)
            else:
                if df_filter_chl['plan'].sum() < 100:
                    order = [df_filter_chl, df_filter_fdl]
                else:
                    order = [df_filter_fdl, df_filter_chl]

                df_filter_dict = pd.concat(order).to_dict('records')
                df_filter_dict_lactose = df_filter_oth.to_dict('records')
                boilings.add_group(df_filter_dict)
                boilings.add_group(df_filter_dict_lactose)
        else:
            df_filter_dict = df_filter.sort_values(by=['weight', 'pack_weight'], ascending=[False, False])\
                .to_dict('records')
            boilings.add_group(df_filter_dict)

        # boilings.add_group(df_filter_dict, is_lactose)
        # boilings.add_group(df_filter_dict)
        # is_lactose = order[0]
    boilings.finish()
    return pd.DataFrame(boilings.boilings), boilings.boiling_number


def handle_salt(df, max_weight=850, min_weight=850, boiling_number=1):
    boilings = Boilings(max_weight=850, min_weight=850, boiling_number=boiling_number)

    for weight, df_grouped_weight in df.groupby('weight'):
        for boiling_id, df_grouped_boiling_id in df_grouped_weight.groupby('boiling_id'):
            new = True
            for group, df_grouped in df_grouped_boiling_id.groupby('group'):
                rubber_sku_exist = any([x for x in df_grouped.to_dict('records')
                                        if 'Терка' in x['sku'].form_factor.name])
                if rubber_sku_exist:
                    df_grouped_sul = [x for x in df_grouped.to_dict('records')
                                      if x['sku'].form_factor.name == 'Терка Сулугуни']
                    df_grouped_moz = [x for x in df_grouped.to_dict('records')
                                      if x['sku'].form_factor.name == 'Терка Моцарелла']

                    boilings.add_group(df_grouped_sul, True)
                    boilings.add_group(df_grouped_moz, True)
                    new = True
                else:
                    df_grouped_dict = df_grouped.sort_values(by=['weight', 'pack_weight'], ascending=[True, False]) \
                        .to_dict('records')
                    boilings.add_group(df_grouped_dict, new)
                    new = False

    boilings.finish()
    return pd.DataFrame(boilings.boilings), boilings.boiling_number


class Boilings:
    def __init__(self, max_weight=1000, min_weight=1000, boiling_number=0):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.boiling_number = boiling_number
        self.boilings = []
        self.cur_boiling = []

    def cur_sum(self):
        if self.cur_boiling:
            return sum([x['plan'] for x in self.cur_boiling])
        return 0

    def add(self, sku):
        while sku['plan'] > 0:
            remainings = self.max_weight - self.cur_sum()
            boiling_weight = min(remainings, sku['plan'])
            new_boiling = deepcopy(sku)
            new_boiling['plan'] = boiling_weight
            new_boiling['tag'] = 'main'
            new_boiling['id'] = self.boiling_number
            sku['plan'] -= boiling_weight
            self.cur_boiling.append(new_boiling)
            if boiling_weight == remainings:
                self.boilings += self.cur_boiling
                self.boiling_number += 1
                self.cur_boiling = []

    def finish(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_remainings(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_group(self, skus, new=True):
        if new:
            self.add_remainings()
        for sku in skus:
            self.add(sku)


class MergedBoilings:
    def __init__(self, max_weight=1000, min_weight=1000, boiling_number=0):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.boiling_number = boiling_number
        self.boilings = []
        self.cur_boiling = []

    def add_sku(self, sku):
        new_boiling = deepcopy(sku)
        new_boiling['plan'] = sku['plan']
        new_boiling['tag'] = 'main'
        new_boiling['id'] = self.boiling_number
        self.cur_boiling.append(new_boiling)

    def finish(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_group(self, skus, new=True):
        if new:
            self.finish()
        for sku in skus:
            self.add_sku(sku)


def draw_boiling_names(wb):
    boilings = db.session.query(Boiling).all()
    boiling_names = list(set([x.to_str() for x in boilings]))
    boiling_type_sheet = wb['Типы варок']
    draw_row(boiling_type_sheet, 1, ['-'], font_size=8)
    cur_i = 2
    for boiling_name in boiling_names:
        draw_row(boiling_type_sheet, cur_i, [boiling_name], font_size=8)
        cur_i += 1


def draw_skus(wb, sheet_name, data_sku):
    grouped_skus = data_sku[sheet_name]
    grouped_skus.sort(key=lambda x: x.name, reverse=False)
    sku_sheet_name = '{} SKU'.format(sheet_name)
    sku_sheet = wb[sku_sheet_name]

    draw_row(sku_sheet, 1, ['-', '-'], font_size=8)
    cur_i = 2

    for group_sku in grouped_skus:
        draw_row(sku_sheet, cur_i, [group_sku.name, group_sku.made_from_boilings[0].to_str()], font_size=8)
        cur_i += 1


def draw_constructor_template(df, file_name, wb, df_extra_packing):
    skus = db.session.query(SKU).all()
    form_factors = db.session.query(FormFactor).all()
    data_sku = {'Вода': [x for x in skus if x.made_from_boilings[0].boiling_type == 'water'],
                'Соль': [x for x in skus if x.made_from_boilings[0].boiling_type == 'salt']}

    draw_boiling_names(wb)
    extra_packing_sheet = wb['Дополнительная фасовка']
    cur_i = 2
    for value in df_extra_packing.values:
        if value[0] in [sku.name for sku in skus if not sku.packing_by_request]:
            draw_row(extra_packing_sheet, cur_i, value, font_size=8)
            cur_i += 1

    boiling_form_factor_sheet = wb['Форм фактор плавления']
    cur_i = 1
    for value in sorted(form_factors, key=lambda x: x.weight_with_line):
        draw_row(boiling_form_factor_sheet, cur_i, [value.weight_with_line], font_size=8)
        cur_i += 1

    for sheet_name in ['Соль', 'Вода']:
        boiling_sheet = wb[sheet_name]
        draw_skus(wb, sheet_name, data_sku)

        cur_i = 2
        values = []
        sku_names = [x.name for x in data_sku[sheet_name]]
        df_filter = df[df['name'].isin(sku_names)].copy()
        for id, grp in df_filter.groupby('id', sort=False):
            for i, row in grp.iterrows():
                v = []
                v += list(row.values)
                v += ['']
                values.append(v[:-1])
            values.append(['-'] * (len(df_filter.columns) + 1))

        for v in values:
            if v[0] == '-':
                # ids = [1, 2, 3, 4, 5, 6, 7, 13]
                ids = [2, 3, 4, 5, 6, 7, 8, 14]
                for id in ids:
                    draw_cell(boiling_sheet, id, cur_i, v[0], font_size=8)
                if sheet_name == 'Вода':
                    first_cell_formula = '=IF(N{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN(Q{0})) & ":" & ADDRESS(ROW(),COLUMN(Q{0})))))'.format(
                        cur_i)
                else:
                    first_cell_formula = '=IF(N{0}="-", "-", 1 + MAX(\'Вода\'!$A$2:$A$100) + SUM(INDIRECT(ADDRESS(2,COLUMN(Q{0})) & ":" & ADDRESS(ROW(),COLUMN(Q{0})))))'.format(
                        cur_i)
                draw_cell(boiling_sheet, 1, cur_i, first_cell_formula, font_size=8)
            else:
                colour = get_colour_by_name(v[8], skus)
                if sheet_name == 'Вода':
                    v[1] = '=IF(N{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN(Q{0})) & ":" & ADDRESS(ROW(),COLUMN(Q{0})))))'.format(
                        cur_i)
                else:
                    v[1] = '=IF(N{0}="-", "-", 1 + MAX(\'Вода\'!$A$2:$A$100) + SUM(INDIRECT(ADDRESS(2,COLUMN(Q{0})) & ":" & ADDRESS(ROW(),COLUMN(Q{0})))))'.format(
                        cur_i)
                draw_row(boiling_sheet, cur_i, v[1:-1], font_size=8, color=colour)
                if v[4] == 'Терка':
                    draw_cell(boiling_sheet, 11, cur_i, 2, font_size=8)
                else:
                    draw_cell(boiling_sheet, 11, cur_i, 1, font_size=8)
            cur_i += 1
    new_file_name = '{} План по варкам'.format(file_name.split(' ')[0])
    path = '{}/{}.xlsx'.format(current_app.config['BOILING_PLAN_FOLDER'], new_file_name)

    for sheet in wb.sheetnames:
        wb[sheet].views.sheetView[0].tabSelected = False
    wb.active = 2
    wb.save(path)
    return '{}.xlsx'.format(new_file_name)


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return sku[0].colour
    else:
        return current_app.config['COLOURS']['Default']


def get_boiling_form_factor(sku):
    if sku.form_factor.name != 'Терка':
        return sku.form_factor.weight_with_line
    elif 'хачапури' in sku.name:
        return '{}: {}'.format(sku.line.name_short, 0.37)
    else:
        return '{}: {}'.format(sku.line.name_short, 0.46)
