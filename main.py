from load import load
from prepare import prepare
from figures import walltime, tuna
import pandas as pd


df_uni = load("responses-uni.txt")
df_ptc = load("responses-ptc.txt")

additionals_uni = prepare(df_uni, "stats-uni.txt")
additionals_ptc = prepare(df_ptc, "stats-ptc.txt")

df = pd.concat([df_uni, df_ptc])
print(
    "len(df_uni.index): {}, len(df_ptc.index): {}, len(df.index): {}".format(
        len(df_uni.index), len(df_ptc.index), len(df.index)
    )
)
walltime(df)

tuna(df_uni, additionals_uni, "tuna_uni.png")
tuna(df_ptc, additionals_ptc, "tuna_ptc.png")
