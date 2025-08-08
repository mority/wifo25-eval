from util import mam
from enum import Enum
import pandas as pd

service_start = pd.Timedelta(hours=4)
service_end = pd.Timedelta(minutes=1439)


def find_midnight(itineraries: list) -> pd.Timestamp | None:
    if not itineraries:
        return None
    return (
        pd.Timestamp(itineraries[0]["startTime"]).tz_convert("Europe/Berlin").floor("d")
    )


def find_next(t: pd.Timestamp, itineraries: list) -> list[pd.Timestamp]:
    next_arr = pd.Timestamp.max.tz_localize("Europe/Berlin")
    next_dep = pd.Timestamp.max.tz_localize("Europe/Berlin")
    for i in itineraries:
        dep = pd.Timestamp(i["startTime"]).tz_convert("Europe/Berlin")
        arr = pd.Timestamp(i["endTime"]).tz_convert("Europe/Berlin")
        if t <= dep and arr < next_arr:
            next_dep = dep
            next_arr = arr
    if next_arr == pd.Timestamp.max.tz_localize("Europe/Berlin"):
        return []
    else:
        return [next_dep, next_arr]


def tuna(itineraries: list) -> list[pd.Timedelta | None]:
    ret: list[pd.Timedelta | None] = [None] * 1440
    mn = find_midnight(itineraries)
    if mn is None:
        return ret
    journey: list[pd.Timestamp] = []
    for t in pd.date_range(
        start=mn + service_start, end=mn + service_end, freq="min", inclusive="both"
    ):
        if not journey or journey[0] < t:
            journey = find_next(t, itineraries)
        if not journey:
            break
        ret[mam(t)] = journey[1] - t
    return ret


def normalized_delta_tuna(
    ref: list[pd.Timedelta | None], cmp: list[pd.Timedelta | None]
) -> list[float]:
    delta: list[float] = []
    for r, c in zip(ref, cmp):
        if not r is None and not c is None:
            delta.append((r - c) / r)
        elif r is None and c is None:
            delta.append(0)
        elif r is None and not c is None:
            delta.append(1)
        else:
            delta.append(-1)

    return delta
