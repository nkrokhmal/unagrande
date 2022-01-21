from app.imports.runtime import *
from app.scheduler.time import *
from app.scheduler.parsing_new import *


def parse_schedule(ws_obj):
    df = utils.read_merged_cells_df(ws_obj, basic_features=False)

    with code('Find time'):
        # find time index rows
        time_index_rows = df[df['label'].astype(str).str.contains('График')]['x1'].unique()
        row = time_index_rows[0]

        # extract time
        hour = int(df[(df["x0"] == 5) & (df["x1"] == row)].iloc[0]["label"])
        if hour >= 12:
            # yesterday
            hour -= 24
        start_time = cast_time(hour * 12)

    with code('find cheese makers rows'):
        df1 = df[df['x0'] >= 5]  # column header out

        # find cheese_maker_rows
        rows = []
        for row_num in df1['x1'].unique():
            row_labels = [str(row['label']) for i, row in df1[df1['x1'] == row_num].iterrows()]
            row_labels = [re.sub(r'\s+', ' ', label) for label in row_labels if label]

            if {'налив/внесение закваски', 'схватка'}.issubset(set(row_labels)):
                rows.append(row_num - 1)

    parsed_schedule = {'boilings': []}
    for i, row in enumerate(rows):
        with code('find line blocks'):
            def _filter_func(group):
                try:
                    return utils.is_int_like(group.iloc[0]["label"].split(" ")[0])
                except:
                    return False


            def _split_func(row):
                try:
                    return utils.is_int_like(row["label"].split(" ")[0])
                except:
                    return False

            line_blocks = parse_line(df, row, split_criteria=basic_criteria(max_length=2, split_func=_split_func))
            line_blocks = [line_block for line_block in line_blocks if _filter_func(line_block)]
        with code('expand blocks'):
            def expand_block(df, df_block):
                return df[(df['x1'].isin([df_block['x1'].min(), df_block['x1'].min() + 1])) &
                          (df_block['x0'].min() <= df['x0']) &
                          (df['x0'] < df_block['y0'].max())]

            boiling_dfs = [expand_block(df, line_block) for line_block in line_blocks]

        with code('Convert boilings to dictionaries'):
            for boiling_df in boiling_dfs:
                boiling = boiling_df.set_index('label').to_dict(orient='index')
                boiling = {'blocks': {k: [v['x0'] + cast_t(start_time), v['y0'] + cast_t(start_time)] for k, v in boiling.items()}}

                try:
                    boiling['boiling_id'] = int(boiling_df.iloc[0]["label"].split(" ")[0])
                except Exception as e:
                    boiling['boiling_id'] = None
                boiling['interval'] = [boiling_df['x0'].min() + cast_t(start_time), boiling_df['y0'].max() + cast_t(start_time)]
                boiling['interval_time'] = [cast_time(boiling_df['x0'].min() + cast_t(start_time)), cast_time(boiling_df['y0'].max() + cast_t(start_time))]
                boiling['line'] = i + 1

                parsed_schedule['boilings'].append(boiling)

    return parsed_schedule


def test():
    fn = os.path.join(basedir, 'app/data/static/samples/outputs/by_department/mozzarella/Расписание моцарелла 8.xlsx')
    print(pd.DataFrame(parse_schedule((fn, 'Расписание'))))


if __name__ == '__main__':
    test()