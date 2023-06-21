from .boilings import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.make_schedule_from_boilings import *
from app.scheduler.mozzarella.algo.stats import *


def _find_optimal_cleanings_combination_by_schedule(schedule):

    # - Get full cleaning duration

    full_cleaning_length = cast_model(Washer, "Длинная мойка термизатора").time

    # - Unfold boilings

    boilings = schedule["master"]["boiling", True]
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))

    # - Get dataframe with all boilings and their properties

    values = [
        [
            b1.props['boiling_id'],
            b1["pouring"]["first"]["termizator"].x[0],
            b1["pouring"]["first"]["termizator"].y[0],
            b1.props["boiling_group_df"].iloc[0]["group_id"],
            b1.props["boiling_group_df"].iloc[0]["line"].name,
        ]
        for b1, b2 in utils.iter_pairs(boilings, method="any_suffix")
    ]
    df = pd.DataFrame(values, columns=['boiling_id', "x", "y", "group_id", "line_name"])

    # - Calc time_till_next_boiling - time between current boiling and next boiling

    df["time_till_next_boiling"] = (df["x"].shift(-1) - df["y"]).fillna(0).astype(int)

    # - Calc conflict_time - main objective (how much we lose by adding a cleaning here approximately)

    df["conflict_time"] = np.where(
        df["time_till_next_boiling"] < full_cleaning_length,
        full_cleaning_length - df["time_till_next_boiling"],
        0,
    )

    # - Calc is_water_done - has water been finished at this point

    df["is_water_done"] = df["line_name"]
    df["is_water_done"] = np.where(df["is_water_done"] == "Моцарелла в воде", True, np.nan)
    df["is_water_done"] = df["is_water_done"].fillna(method="bfill")
    df["is_water_done"] = df["is_water_done"].shift(-1).fillna(0)
    df["is_water_done"] = df["is_water_done"].astype(bool)
    df["is_water_done"] = ~df["is_water_done"]

    # - Get cleanings

    def _is_cleaning_combination_fit(cleaning_combination):
        # check that distance between boilings without cleaning is less than 15 hours

        separators = [-1] + list(cleaning_combination) + [df.index[-1]]
        for s1, s2 in utils.iter_pairs(separators):
            group = df.loc[s1 + 1 : s2]

            group_length = group.iloc[-1]["y"] - group.iloc[0]["x"]
            if group_length > cast_t("15:00"):
                return False
        return True

    # - Find first combination that fits

    for n_cleanings in range(5):
        # find first available combination

        # - Get all available combinations

        available_combinations = [
            combo
            for combo in itertools.combinations(range(len(df) - 1), n_cleanings)
            if _is_cleaning_combination_fit(combo)
        ]

        # - Continue looking if no available combinations

        if not available_combinations:
            continue

        # - If available combinations exist and n_cleanings == 0, then we don't need any cleanings

        if n_cleanings == 0:
            # no cleanings needed, all is good

            return {}

        values1 = [
            [
                combination,
                sum(df.loc[s]["conflict_time"] for s in combination),
                df.loc[combination[0]]["is_water_done"],
            ]
            for combination in available_combinations
        ]

        df1 = pd.DataFrame(values1, columns=["combo", "total_conflict_time", "is_water_done"])

        # set priorities
        df1 = df1.sort_values(by=["total_conflict_time"], ascending=True)
        df1 = df1.sort_values(by=["is_water_done"], ascending=False)

        # take first one
        combo = df1.iloc[0]["combo"]
        return {df.loc[s]["group_id"]: "short" for s in combo}

    raise Exception("Failed to fill cleanings")


def find_optimal_cleanings(boiling_plan_df, start_times=None, **make_schedule_kwargs):
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    boilings = make_boilings(boiling_plan_df)
    schedule = make_schedule_from_boilings(boilings, start_times=start_times, **make_schedule_kwargs)
    return _find_optimal_cleanings_combination_by_schedule(schedule)
