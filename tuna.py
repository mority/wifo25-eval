from load import load
from util import uses_taxi, mam

import pandas as pd
from datetime import date

day_start = pd.Timedelta(hours=4)
day_end = pd.Timedelta(minutes=1439)


def find_date(itineraries: list) -> date | None:
    if not itineraries:
        return None
    return pd.Timestamp(itineraries[0]["startTime"]).tz_convert("Europe/Berlin").date()


def find_next(t: pd.Timestamp, itineraries: list) -> list[pd.Timestamp]:
    next_arr = pd.Timestamp.max
    next_dep = pd.Timestamp.max
    for i in itineraries:
        dep = pd.Timestamp(i["startTime"]).tz_convert("Europe/Berlin")
        arr = pd.Timestamp(i["endTime"]).tz_convert("Europe/Berlin")
        if t <= dep and arr < next_arr:
            next_dep = dep
            next_arr = arr
    if next_arr == pd.Timestamp.max:
        return []
    else:
        return [next_dep, next_arr]


def tuna(itineraries: list) -> list[pd.Timedelta | None]:
    ret: list[pd.Timedelta | None] = [None] * 1440
    d = find_date(itineraries)
    if d is None:
        return ret
    journey: list[pd.Timestamp] = []
    for t in pd.date_range(
        start=d + day_start, end=d + day_end, freq="min", inclusive="both"
    ):
        if not journey or journey[0] < t:
            journey = find_next(t, itineraries)
        if not journey:
            break
        ret[mam(t)] = journey[1] - t
    return ret


df = load()
tuna = [0] * 1440
print(type(df.at[0, "itineraries"][0]["startTime"]))
