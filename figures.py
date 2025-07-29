import json
import pandas as pd
import plotly.express as px

data = []

with open("responses.txt") as f:
    for l in f:
        data.append(json.loads(l))

df = pd.DataFrame.from_dict(pd.json_normalize(data), orient='columns')
df.columns = df.columns.str.replace(r'debugOutput.', '')

df.rename(
    columns={"mixing_time": "Mixing", "whitelist_time": "2. Verfügbarkeitsprüfung", "routing_time": "ÖV-Routing",
             "blacklist_time": "1. Verfügbarkeitsprüfung", "init_time": "Offset-Routing"}, inplace=True)

df['Gesamtzeit'] = df['Mixing'] + df['2. Verfügbarkeitsprüfung'] + df['ÖV-Routing'] + df['1. Verfügbarkeitsprüfung'] + \
                   df[
                       'Offset-Routing']

df.sort_values(by='Gesamtzeit', ignore_index=True, inplace=True)

fig = px.bar(df, y=['Mixing', '2. Verfügbarkeitsprüfung', 'ÖV-Routing', '1. Verfügbarkeitsprüfung', 'Offset-Routing'])
fig.update_layout(xaxis_title="Anfragen", xaxis_visible=False, yaxis_title="Wall-Time [ms]",
                  legend_title="Abschnitt",
                  legend_traceorder="reversed")
fig.show()
