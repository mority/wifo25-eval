from load import load
from prepare import prepare
from figures import figures

df = load()
df_mam = prepare(df)
figures(df, df_mam)
