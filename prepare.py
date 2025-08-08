import pandas as pd

from util import uses_taxi
from tuna import tuna, normalized_delta_tuna


def prepare(df):
    df.columns = df.columns.str.replace(r"debugOutput.", "")
    df.rename(
        columns={
            "mixing_time": "Mixing",
            "whitelist_time": "2. Verfügbarkeitsprüfung",
            "routing_time": "ÖV-Routing",
            "blacklist_time": "1. Verfügbarkeitsprüfung",
            "init_time": "Offset-Routing",
        },
        inplace=True,
    )

    df["query_id"] = list(range(len(df.index)))

    df["Gesamtzeit"] = (
        df["Mixing"]
        + df["2. Verfügbarkeitsprüfung"]
        + df["ÖV-Routing"]
        + df["1. Verfügbarkeitsprüfung"]
        + df["Offset-Routing"]
    )

    print(
        "Responses without time since direct walk is below threshold of 5 minutes: {}".format(
            pd.isnull(df["Gesamtzeit"]).sum()
        )
    )
    print(
        "Therefore, n is {}".format(len(df.index) - pd.isnull(df["Gesamtzeit"]).sum())
    )

    df["Offset-Routing %"] = df["Offset-Routing"] / df["Gesamtzeit"] * 100
    df["1. Verfügbarkeitsprüfung %"] = (
        df["1. Verfügbarkeitsprüfung"] / df["Gesamtzeit"] * 100
    )
    df["ÖV-Routing %"] = df["ÖV-Routing"] / df["Gesamtzeit"] * 100
    df["2. Verfügbarkeitsprüfung %"] = (
        df["2. Verfügbarkeitsprüfung"] / df["Gesamtzeit"] * 100
    )
    df["Mixing %"] = df["Mixing"] / df["Gesamtzeit"] * 100

    df["n_taxis_init"] = (
        df["init_direct_odm_rides"]
        + df["init_first_mile_odm_rides"]
        + df["init_last_mile_odm_rides"]
    )
    df["n_taxis_blacklist"] = (
        df["blacklist_direct_odm_rides"]
        + df["blacklist_first_mile_odm_rides"]
        + df["blacklist_last_mile_odm_rides"]
    )
    df["n_taxis_routing"] = (
        df["routing_direct_odm_rides"]
        + df["routing_first_mile_odm_rides"]
        + df["routing_last_mile_odm_rides"]
    )
    df["n_taxis_whitelist"] = (
        df["whitelist_direct_odm_rides"]
        + df["whitelist_first_mile_odm_rides"]
        + df["whitelist_last_mile_odm_rides"]
    )

    df["bl_per_taxi"] = df["1. Verfügbarkeitsprüfung"] / df["n_taxis_init"]
    df["wl_per_taxi"] = df["2. Verfügbarkeitsprüfung"] / df["n_taxis_routing"]

    itineraries = []
    for row in df.itertuples():
        itineraries += row.itineraries
    df_itineraries = pd.DataFrame(itineraries)

    df_itineraries["uses_taxi"] = df_itineraries["legs"].apply(uses_taxi)

    df_mam = pd.DataFrame(
        {"pt": [0] * 1440, "taxi": [0] * 1440, "pt_by_taxi": [0] * 1440}
    )
    for i in df_itineraries.itertuples():
        for leg in i.legs:
            col = "pt_by_taxi" if i.uses_taxi else "pt"
            if leg["mode"] == "ODM":
                col = "taxi"
            for t in pd.date_range(
                start=leg["startTime"], end=leg["endTime"], freq="min", inclusive="left"
            ):
                local_t = t.tz_convert("Europe/Berlin").time()
                mam = local_t.hour * 60 + local_t.minute
                df_mam.at[mam, col] += 1

    df["tuna"] = df["itineraries"].apply(tuna)
    df["itineraries_pt"] = df["itineraries"].apply(
        lambda l: list(filter(lambda i: not uses_taxi(i["legs"]), l))
    )
    df["tuna_pt"] = df["itineraries_pt"].apply(tuna)

    df["delta_tuna"] = df.apply(
        lambda row: normalized_delta_tuna(row["tuna_pt"], row["tuna"]), axis=1
    )

    return df_mam
