from load import load
from prepare import prepare
from figures import walltime, tuna
import pandas as pd

df_uni: pd.DataFrame = load("responses-uni.txt")
df_ptc: pd.DataFrame = load("responses-ptc.txt")

print("preparing uni")
additionals_uni = prepare(df_uni)
print("preparing ptc")
additionals_ptc = prepare(df_ptc)

df = pd.concat([df_uni, df_ptc])
print(
    "len(df_uni.index): {}, len(df_ptc.index): {}, len(df.index): {}".format(
        len(df_uni.index), len(df_ptc.index), len(df.index)
    )
)
walltime(df)

tuna(df_uni, additionals_uni)
tuna(df_ptc, additionals_ptc)
