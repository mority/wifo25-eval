import pandas as pd
import numpy as np

from util import uses_taxi, is_direct_taxi, without_pt, without_taxi
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

    df["Gesamt"] = (
        df["Mixing"]
        + df["2. Verfügbarkeitsprüfung"]
        + df["ÖV-Routing"]
        + df["1. Verfügbarkeitsprüfung"]
        + df["Offset-Routing"]
    )

    print(
        "Responses without time since direct walk is below threshold of 5 minutes: {}".format(
            pd.isnull(df["Gesamt"]).sum()
        )
    )
    df.drop(df[pd.isnull(df.Gesamt)].index, inplace=True)
    print("After dropping these, n is {}".format(len(df.index)))

    df["Offset-Routing %"] = df["Offset-Routing"] / df["Gesamt"] * 100
    df["1. Verfügbarkeitsprüfung %"] = (
        df["1. Verfügbarkeitsprüfung"] / df["Gesamt"] * 100
    )
    df["ÖV-Routing %"] = df["ÖV-Routing"] / df["Gesamt"] * 100
    df["2. Verfügbarkeitsprüfung %"] = (
        df["2. Verfügbarkeitsprüfung"] / df["Gesamt"] * 100
    )
    df["Mixing %"] = df["Mixing"] / df["Gesamt"] * 100

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
    n_responses_without_taxi = 0
    n_responses_without_pt = 0
    n_responses_empty = 0
    for row in df.itertuples():
        itineraries += row.itineraries
        if without_taxi(row.itineraries):
            n_responses_without_taxi += 1
        if without_pt(row.itineraries):
            n_responses_without_pt += 1
        if len(row.itineraries) == 0:
            n_responses_empty += 1
    print(
        "empty responses: {}/{} ({:.2f}%)\n"
        "responses without pt: {}/{} ({:.2f}%)\n"
        "responses without taxi: {}/{} ({:.2f}%)".format(
            n_responses_empty,
            len(df.index),
            n_responses_empty / len(df.index) * 100,
            n_responses_without_pt,
            len(df.index),
            n_responses_without_pt / len(df.index) * 100,
            n_responses_without_taxi,
            len(df.index),
            n_responses_without_taxi / len(df.index) * 100,
        )
    )

    df_itineraries = pd.DataFrame(itineraries)
    df_itineraries["uses_taxi"] = df_itineraries["legs"].apply(uses_taxi)
    df_itineraries["is_direct_taxi"] = df_itineraries["legs"].apply(is_direct_taxi)
    n_itineraries_total = len(df_itineraries.index)
    n_itineraries_uses_taxi = df_itineraries["uses_taxi"].value_counts()[True]
    n_itineraries_direct_taxi = df_itineraries["is_direct_taxi"].value_counts()[True]
    n_itineraries_pt_only = n_itineraries_total - n_itineraries_uses_taxi
    n_itineraries_pt_taxi = n_itineraries_uses_taxi - n_itineraries_direct_taxi
    percentage_itineraries_uses_taxi = (
        n_itineraries_uses_taxi / n_itineraries_total * 100
    )
    percentage_itineraries_direct_taxi = (
        n_itineraries_direct_taxi / n_itineraries_total * 100
    )
    percentage_itineraries_pt_only = n_itineraries_pt_only / n_itineraries_total * 100
    percentage_itineraries_pt_taxi = n_itineraries_pt_taxi / n_itineraries_total * 100

    print(
        "itineraries total: {}\nitineraries pt-only: {} ({:.2f}%)\nitineraries uses_taxi: {} ({:.2f}%)\nitineraries pt-taxi: {} ({:.2f}%)\nitineraries taxi-only: {} ({:.2f}%)".format(
            n_itineraries_total,
            n_itineraries_pt_only,
            percentage_itineraries_pt_only,
            n_itineraries_uses_taxi,
            percentage_itineraries_uses_taxi,
            n_itineraries_pt_taxi,
            percentage_itineraries_pt_taxi,
            n_itineraries_direct_taxi,
            percentage_itineraries_direct_taxi,
        )
    )

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

    delta_tuna = pd.DataFrame(np.vstack(df["delta_tuna"]))

    delta_tuna_stats = delta_tuna.apply(
        lambda col: np.append(
            np.percentile(col, [10, 20, 30, 40, 50, 60, 70, 80, 90]), np.mean(col)
        )
    ).T
    delta_tuna_stats.columns = [
        "10%",
        "20%",
        "30%",
        "40%",
        "50%",
        "60%",
        "70%",
        "80%",
        "90%",
        "mean",
    ]

    return df_mam, delta_tuna, delta_tuna_stats
