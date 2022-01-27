from app.imports.runtime import *
from app.scheduler.time import *
from app.scheduler.parsing_new import *

COLUMN_SHIFT = 5 # header 4 + 1 for one-indexing

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

    parsed_schedule = {'boilings': []}
    with code('find line blocks'):
        def _filter_func(group):
            try:
                return 'анализы' in group.iloc[0]['label']
            except:
                return False

        def _split_func(prev_row, row):
            try:
                return 'анализы' in row["label"].lower() or 'фасовка' in row['label'].lower()
            except:
                return False

        line_blocks = parse_line(df, 2, split_criteria=basic_criteria(split_func=_split_func))
        line_blocks = [line_block for line_block in line_blocks if _filter_func(line_block)]
    boiling_dfs = line_blocks

    with code('Convert boilings to dictionaries'):
        for boiling_df in boiling_dfs:
            boiling = boiling_df.set_index('label').to_dict(orient='index')
            boiling = {'blocks': {k: [v['x0'] + cast_t(start_time) - COLUMN_SHIFT, v['y0'] + cast_t(start_time) - COLUMN_SHIFT] for k, v in boiling.items()}}

            boiling['boiling_id'] = None

            boiling['interval'] = [boiling_df['x0'].min() + cast_t(start_time) - COLUMN_SHIFT,
                                   boiling_df['y0'].max() + cast_t(start_time) - COLUMN_SHIFT]
            boiling['interval_time'] = list(map(cast_human_time, boiling['interval']))
            parsed_schedule['boilings'].append(boiling)

    return parsed_schedule


def test():
    fn = os.path.join(basedir, 'app/data/static/samples/outputs/by_department/butter/Расписание масло 1.xlsx')
    print(pd.DataFrame(parse_schedule((fn, 'Расписание'))))


if __name__ == '__main__':
    test()