from load import load
from util import uses_taxi
import pandas as pd
import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

pio.templates.default = 'plotly_white'

df = load()
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

df['Offset-Routing %'] = df['Offset-Routing'] / df['Gesamtzeit'] * 100
df['1. Verfügbarkeitsprüfung %'] = df['1. Verfügbarkeitsprüfung'] / \
    df['Gesamtzeit'] * 100
df['ÖV-Routing %'] = df['ÖV-Routing'] / df['Gesamtzeit'] * 100
df['2. Verfügbarkeitsprüfung %'] = df['2. Verfügbarkeitsprüfung'] / \
    df['Gesamtzeit'] * 100
df['Mixing %'] = df['Mixing'] / df['Gesamtzeit'] * 100
relative_keys = ['Offset-Routing %', '1. Verfügbarkeitsprüfung %', 'ÖV-Routing %', '2. Verfügbarkeitsprüfung %',
                 'Mixing %']

df['n_taxis_init'] = df['init_direct_odm_rides'] + \
    df['init_first_mile_odm_rides'] + df['init_last_mile_odm_rides']
df['n_taxis_blacklist'] = df['blacklist_direct_odm_rides'] + \
    df['blacklist_first_mile_odm_rides'] + \
    df['blacklist_last_mile_odm_rides']
df['n_taxis_routing'] = df['routing_direct_odm_rides'] + \
    df['routing_first_mile_odm_rides'] + df['routing_last_mile_odm_rides']
df['n_taxis_whitelist'] = df['whitelist_direct_odm_rides'] + \
    df['whitelist_first_mile_odm_rides'] + \
    df['whitelist_last_mile_odm_rides']

scatter_symbols = ['diamond', 'square', 'circle', 'triangle-up', 'x']

df['bl_per_taxi'] = df['1. Verfügbarkeitsprüfung'] / df['n_taxis_init']
df['wl_per_taxi'] = df['2. Verfügbarkeitsprüfung'] / df['n_taxis_routing']

itineraries = []
for row in df.itertuples():
    itineraries += row.itineraries
df_itineraries = pd.DataFrame(itineraries)


df_itineraries['uses_taxi'] = df_itineraries['legs'].apply(uses_taxi)

df_mam = pd.DataFrame({'pt': [0] * 1440, 'taxi': [0] * 1440, 'pt_by_taxi': [0] * 1440})
for i in df_itineraries.itertuples():
    for leg in i.legs:
        col = 'pt_by_taxi' if i.uses_taxi else 'pt'
        if leg['mode'] == 'ODM':
            col = 'taxi'
        for t in pd.date_range(start=leg['startTime'], end=leg['endTime'], freq='min', inclusive='left'):
            local_t = t.tz_convert('Europe/Berlin').time()
            mam = local_t.hour * 60 + local_t.minute
            df_mam.at[mam, col] += 1


def walltime_stacked_bar():
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


def walltime_violin():
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


def absolute_section_time_scatter():
    absolute_keys = ['Offset-Routing', '1. Verfügbarkeitsprüfung', 'ÖV-Routing', '2. Verfügbarkeitsprüfung',
                     'Mixing']
    df.sort_values(by='Gesamtzeit', ignore_index=True, inplace=True)
    scatter_absolute = go.Figure()
    for k, s in zip(absolute_keys, scatter_symbols):
        scatter_absolute.add_trace(go.Scatter(
            name=k, mode='markers', x=df['Gesamtzeit'], y=df[k], marker=dict(symbol=s)))
    scatter_absolute.update_layout(
        font=dict(family='Arial', size=14), yaxis_title="Zeit in Abschnitt [ms]", xaxis_title="Gesamte Wall-Time [ms]", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    scatter_absolute.show()


def relative_section_time_scatter():
    scatter_relative = go.Figure()
    for k, s in zip(relative_keys, scatter_symbols):
        scatter_relative.add_trace(go.Scatter(
            name=k, mode='markers', x=df['Gesamtzeit'], y=df[k], marker=dict(symbol=s)))
    scatter_relative.update_layout(
        yaxis_title='Anteil in %', xaxis_title="Gesamte Wall-Time [ms]", legend=dict(yanchor="top", y=.5, xanchor="right", x=.99))
    scatter_relative.show()


def taxi_rides_per_section_violin():
    violin_taxis = make_subplots(rows=1, cols=2)
    violin_taxis.add_trace(go.Violin(
        y=df['n_taxis_init'], name='Initial', box_visible=True, meanline_visible=True), row=1, col=1)
    violin_taxis.add_trace(go.Violin(
        y=df['n_taxis_blacklist'], name='1. Verfügbark.', box_visible=True, meanline_visible=True), row=1, col=1)
    violin_taxis.add_trace(go.Violin(
        y=df['n_taxis_routing'], name='Routing', box_visible=True, meanline_visible=True), row=1, col=2)
    violin_taxis.add_trace(go.Violin(
        y=df['n_taxis_whitelist'], name='2. Verfügbark.', box_visible=True, meanline_visible=True), row=1, col=2)
    violin_taxis.update_layout(
        yaxis_title='Anzahl Taxifahrten', showlegend=False)
    violin_taxis.show()


def walltime_per_taxi_ride():
    violin_per_taxi = make_subplots(rows=1, cols=2)
    violin_per_taxi.add_trace(go.Violin(
        y=df['bl_per_taxi'], name='1. Verfügbarkeitsprüfung', box_visible=True, meanline_visible=True), row=1, col=1)
    violin_per_taxi.add_trace(go.Violin(
        y=df['wl_per_taxi'], name='2. Verfügbarkeitsprüfung', box_visible=True, meanline_visible=True), row=1, col=2)
    violin_per_taxi.update_layout(
        yaxis_title='Zeit pro angefragtem Taxi [µs]', showlegend=False)
    violin_per_taxi.show()

def mam_fig():
    mam_fig = px.bar(df_mam, y=['pt', 'pt_by_taxi'])
    mam_fig.update_layout(bargap=0, xaxis_title="Tageszeit", xaxis_tickmode='array',
                              xaxis_tickvals=list(range(0, 1440, 60)),
                              xaxis_ticktext=['{:02d}:00'.format(x // 60) for x in range(0,1440,60)], xaxis_ticks='outside', yaxis_title="Anzahl Verbindungen", yaxis_dtick=1000,
                              legend=dict(
                                  traceorder="reversed",
                                  yanchor="top",
                                  y=0.99,
                                  xanchor="left",
                                  x=0.01
                              ))
    mam_fig.show()

# walltime_stacked_bar()
# walltime_violin()
# absolute_section_time_scatter()
# relative_section_time_scatter()
# taxi_rides_per_section_violin()
# walltime_per_taxi_ride()
mam_fig()

# for c in list(df.columns):
#     print(c)
