import json
import pandas as pd
import math
import plotly.express as px

data = []

with open("responses.txt") as f:
    for l in f:
        data.append(json.loads(l))

df = pd.json_normalize(data)
df.columns = df.columns.str.replace(r'debugOutput.', '')
df.rename(
    columns={"mixing_time": "Mixing", "whitelist_time": "2. Verfügbarkeitsprüfung", "routing_time": "ÖV-Routing",
             "blacklist_time": "1. Verfügbarkeitsprüfung", "init_time": "Offset-Routing"}, inplace=True)

quantile_vals = [math.floor(len(df.index) * 0.25), math.floor(len(df.index) * 0.5), math.floor(len(df.index) * 0.75),
                 math.floor(len(df.index) * 0.9), math.floor(len(df.index) * 0.99)]
quantile_text = ['25%', '50%', '75%', '90%', '99%']

df['Gesamtzeit'] = df['Mixing'] + df['2. Verfügbarkeitsprüfung'] + df['ÖV-Routing'] + df['1. Verfügbarkeitsprüfung'] + \
                   df[
                       'Offset-Routing']

df.sort_values(by='Gesamtzeit', ignore_index=True, inplace=True)

print('Responses without time since direct walk is below threshold of 5 minutes: {}'.format(
    pd.isnull(df['Gesamtzeit']).sum()))
print('Therefore, n is {}'.format(len(df.index) - pd.isnull(df['Gesamtzeit']).sum()))
print('Total time quantiles:')
print(df.iloc[quantile_vals]['Gesamtzeit'])

fig = px.bar(df, y=['Mixing', '2. Verfügbarkeitsprüfung', 'ÖV-Routing', '1. Verfügbarkeitsprüfung', 'Offset-Routing'])
fig.update_layout(bargap=0, xaxis_title="Anfragen Quantile", xaxis_tickmode='array',
                  xaxis_tickvals=quantile_vals,
                  xaxis_ticktext=quantile_text, xaxis_ticks='outside', yaxis_title="Wall-Time [ms]", yaxis_dtick=1000,
                  legend_title="Abschnitt",
                  legend_traceorder="reversed")
fig.show()
