import json
import pandas as pd
import math
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = 'plotly_white'

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
    df['Offset-Routing']

print('Responses without time since direct walk is below threshold of 5 minutes: {}'.format(
    pd.isnull(df['Gesamtzeit']).sum()))
print('Therefore, n is {}'.format(
    len(df.index) - pd.isnull(df['Gesamtzeit']).sum()))


# Stacked Bar Plot
df.sort_values(by='Gesamtzeit', ignore_index=True, inplace=True)
stacked_bar = px.bar(df, y=['Mixing', '2. Verfügbarkeitsprüfung',
                     'ÖV-Routing', '1. Verfügbarkeitsprüfung', 'Offset-Routing'])
stacked_bar.update_layout(bargap=0, xaxis_title="Anfragen Quantile", xaxis_tickmode='array',
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
stacked_bar.show()


# Violin Plots
violin_keys = ['Gesamtzeit', 'Offset-Routing', '1. Verfügbarkeitsprüfung', 'ÖV-Routing', '2. Verfügbarkeitsprüfung',
               'Mixing']
violins = go.Figure()
for k in violin_keys:
    df.sort_values(by=k, ignore_index=True, inplace=True)
    print('{} quantiles:'.format(k))
    print(df[k].quantile(quantiles))
    violins.add_trace(
        go.Violin(y=df[k], name=k, box_visible=True, meanline_visible=True))
violins.update_layout(yaxis_title="Wall-Time [ms]", showlegend=False)
violins.show()


scatter_symbols = ['diamond', 'square', 'circle', 'triangle-up', 'x']

absolute_keys = ['Offset-Routing', '1. Verfügbarkeitsprüfung', 'ÖV-Routing', '2. Verfügbarkeitsprüfung',
                 'Mixing']

# scatter plot absolute
df.sort_values(by='Gesamtzeit', ignore_index=True, inplace=True)
scatter_absolute = go.Figure()
for k, s in zip(absolute_keys, scatter_symbols):
    scatter_absolute.add_trace(go.Scatter(
        name=k, mode='markers', x=df['Gesamtzeit'], y=df[k], marker=dict(symbol=s)))
scatter_absolute.update_layout(
    font=dict(family='Arial', size=14), yaxis_title="Zeit in Abschnitt [ms]", xaxis_title="Gesamte Wall-Time [ms]", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
scatter_absolute.show()

# violin plot absolute
violin_absolute = go.Figure()
for k in absolute_keys:
    violin_absolute.add_trace(
        go.Violin(y=df[k], name=k, box_visible=True, meanline_visible=True))
violin_absolute.update_layout(yaxis_title='Wall-Time [ms]', showlegend=False)
violin_absolute.show()

# get relative times
df['Offset-Routing %'] = df['Offset-Routing'] / df['Gesamtzeit'] * 100
df['1. Verfügbarkeitsprüfung %'] = df['1. Verfügbarkeitsprüfung'] / \
    df['Gesamtzeit'] * 100
df['ÖV-Routing %'] = df['ÖV-Routing'] / df['Gesamtzeit'] * 100
df['2. Verfügbarkeitsprüfung %'] = df['2. Verfügbarkeitsprüfung'] / \
    df['Gesamtzeit'] * 100
df['Mixing %'] = df['Mixing'] / df['Gesamtzeit'] * 100
relative_keys = ['Offset-Routing %', '1. Verfügbarkeitsprüfung %', 'ÖV-Routing %', '2. Verfügbarkeitsprüfung %',
                 'Mixing %']

# scatter plot relative
scatter_relative = go.Figure()
for k, s in zip(relative_keys, scatter_symbols):
    scatter_relative.add_trace(go.Scatter(
        name=k, mode='markers', x=df['Gesamtzeit'], y=df[k], marker=dict(symbol=s)))
scatter_relative.update_layout(
    yaxis_title='Anteil in %', xaxis_title="Gesamte Wall-Time [ms]", legend=dict(yanchor="top", y=.5, xanchor="right", x=.99))
scatter_relative.show()

# violin plot relative
violin_relative = go.Figure()
for k in relative_keys:
    violin_relative.add_trace(
        go.Violin(y=df[k], name=k, box_visible=True, meanline_visible=True))
violin_relative.update_layout(yaxis_title='Anteil in %', showlegend=False)
violin_relative.show()
