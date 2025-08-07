import pandas as pd


def uses_taxi(legs):
    for leg in legs:
        if leg["mode"] == "ODM":
            return True
    return False


def mam(t: pd.Timestamp) -> int:
    return t.hour * 60 + t.minute
