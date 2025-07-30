import json
import pandas as pd
import math
import plotly.express as px
import plotly.graph_objects as go

data = []

with open("responses.txt") as f:
    for l in f:
        data.append(json.loads(l))

df = pd.json_normalize(data)
df.columns = df.columns.str.replace(r'debugOutput.', '')
df.rename(
    columns={"mixing_time": "Mixing", "whitelist_time": "2. Verfügbarkeitsprüfung", "routing_time": "ÖV-Routing",
             "blacklist_time": "1. Verfügbarkeitsprüfung", "init_time": "Offset-Routing"}, inplace=True)

quantiles = [.25, .5, .75, .9, .99, 1]
quantile_index = [math.floor(len(df.index) * 0.25), math.floor(len(df.index) * 0.5), math.floor(len(df.index) * 0.75),
                  math.floor(len(df.index) * 0.9), math.floor(len(df.index) * 0.99)]
quantile_text = ['25%', '50%', '75%', '90%', '99%']

df['query_id'] = list(range(len(df.index)))
df['Gesamtzeit'] = df['Mixing'] + df['2. Verfügbarkeitsprüfung'] + df['ÖV-Routing'] + df['1. Verfügbarkeitsprüfung'] + \
                   df[
                       'Offset-Routing']

print('Responses without time since direct walk is below threshold of 5 minutes: {}'.format(
    pd.isnull(df['Gesamtzeit']).sum()))
print('Therefore, n is {}'.format(len(df.index) - pd.isnull(df['Gesamtzeit']).sum()))

# Stacked Bar Plot
df.sort_values(by='Gesamtzeit', ignore_index=True, inplace=True)
fig = px.bar(df, y=['Mixing', '2. Verfügbarkeitsprüfung', 'ÖV-Routing', '1. Verfügbarkeitsprüfung', 'Offset-Routing'])
fig.update_layout(bargap=0, xaxis_title="Anfragen Quantile", xaxis_tickmode='array',
                  xaxis_tickvals=quantile_index,
                  xaxis_ticktext=quantile_text, xaxis_ticks='outside', yaxis_title="Wall-Time [ms]", yaxis_dtick=1000,
                  legend=dict(
                      title="Abschnitt",
                      traceorder="reversed",
                      yanchor="top",
                      y=0.99,
                      xanchor="left",
                      x=0.01
                  ))
fig.show()

# Violin Plots
fig = go.Figure()
violin_keys = ['Gesamtzeit', 'Offset-Routing', '1. Verfügbarkeitsprüfung', 'ÖV-Routing', '2. Verfügbarkeitsprüfung',
               'Mixing']
for k in violin_keys:
    df.sort_values(by=k, ignore_index=True, inplace=True)
    print('{} quantiles:'.format(k))
    print(df[k].quantile(quantiles))
    fig.add_trace(go.Violin(y=df[k], name=k, box_visible=True, meanline_visible=True))

fig.update_layout(yaxis_title="Wall-Time [ms]", showlegend=False)
fig.show()

# Line Plot
fig = go.Figure()
