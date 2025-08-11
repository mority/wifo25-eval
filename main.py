from load import load
from prepare import prepare
from figures import figures

df = load()
additionals = prepare(df)
figures(df, additionals)
