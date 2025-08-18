import math
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import kaleido
import asyncio


def set_template():
    pio.templates["adjustments"] = go.layout.Template(
        layout=dict(
            font={"size": 20, "family": "Arial"},
            xaxis=dict(title_font={"size": 20}),
            yaxis=dict(title_font={"size": 20}),
        )
    )
    pio.templates.default = "plotly_white+adjustments"


def walltime(df):
    set_template()

    quantiles = [0.25, 0.5, 0.75, 0.9, 0.99, 1]
    quantile_index = [
        math.floor(len(df.index) * 0.25),
        math.floor(len(df.index) * 0.5),
        math.floor(len(df.index) * 0.75),
        math.floor(len(df.index) * 0.9),
        math.floor(len(df.index) * 0.99),
    ]
    quantile_text = ["25%", "50%", "75%", "90%", "99%"]

    df.sort_values(by="Gesamt", ignore_index=True, inplace=True)
    stacked_bar = px.bar(
        df,
        y=[
            "Mixing",
            "2. Verfügbarkeitsprüfung",
            "ÖV-Routing",
            "1. Verfügbarkeitsprüfung",
            "Offset-Routing",
        ],
    )
    stacked_bar.update_layout(
        bargap=0,
        xaxis_title="Anfragen Quantile",
        xaxis_tickmode="array",
        xaxis_tickvals=quantile_index,
        xaxis_ticktext=quantile_text,
        xaxis_ticks="outside",
        yaxis_title="Wall-Time [ms]",
        yaxis_dtick=1000,
        legend=dict(
            title="Abschnitt",
            traceorder="reversed",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
        ),
    )
    stacked_bar.show()

    violin_keys = [
        "Gesamt",
        "Offset-Routing",
        "1. Verfügbarkeitsprüfung",
        "ÖV-Routing",
        "2. Verfügbarkeitsprüfung",
        # "Mixing",
    ]
    violin_names = {
        "Gesamt": "Gesamt",
        "Offset-Routing": "Offset-<br>Routing",
        "1. Verfügbarkeitsprüfung": "1. Verfügbarkeits-<br>prüfung",
        "ÖV-Routing": "ÖV-<br>Routing",
        "2. Verfügbarkeitsprüfung": "2. Verfügbarkeits-<br>prüfung",
    }
    violins = go.Figure()
    for k in violin_keys:
        df.sort_values(by=k, ignore_index=True, inplace=True)
        violins.add_trace(
            go.Violin(
                y=df[k],
                name=violin_names[k],
                box_visible=True,
                meanline_visible=True,
                line_color="black",
                fillcolor="gainsboro",
                spanmode="hard",
                points=False,
            )
        )
    violins.update_layout(
        yaxis=dict(title="Wall-Time [ms]", minallowed=0),
        showlegend=False,
    )
    violins.show()
    violins.write_image("walltime_violins.png", scale=2, width=800, height=600)


def tuna(df, additionals, file_name):
    df_mam, delta_tuna, delta_tuna_stats = additionals
    set_template()

    tuna_line = px.line(delta_tuna_stats)
    tuna_line.update_layout(
        xaxis_title="Tageszeit",
        xaxis_tickmode="array",
        xaxis_tickvals=list(range(0, 1440, 120)),
        xaxis_ticktext=["{:02d}:00".format(x // 60) for x in range(0, 1440, 120)],
        xaxis_ticks="outside",
        yaxis_title="Normalisierter Reisezeitvorteil",
        showlegend=True,
    )
    tuna_line.show()

    x = list(range(1440)) * len(delta_tuna.index)
    y = delta_tuna.to_numpy().flatten()

    tuna_hist = go.Figure()
    tuna_hist.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker_size=1,
            marker_color="black",
            showlegend=False,
        )
    )
    tuna_hist.add_trace(
        go.Histogram2d(
            x=x,
            y=y,
            autobinx=False,
            xbins=dict(start=0, end=1440, size=30),
            autobiny=False,
            ybins=dict(start=-0.0125, end=1.0125, size=0.025),
            colorscale="greys",
        )
    )
    tuna_hist.add_trace(
        go.Scatter(
            x=list(range(1440)),
            y=delta_tuna_stats["mean"],
            line_color="white",
            line_width=5,
            showlegend=False,
        )
    )
    tuna_hist.add_trace(
        go.Scatter(
            x=list(range(1440)),
            y=delta_tuna_stats["mean"],
            line_color="black",
            showlegend=False,
        )
    )
    tuna_hist.update_layout(
        xaxis=dict(
            range=[0, 1440],
            title="Tageszeit",
            tickmode="array",
            tickvals=list(range(0, 1441, 240)),
            ticktext=["{:02d}:00".format(x // 60) for x in range(0, 1441, 240)],
            ticks="outside",
            minor=dict(
                tickmode="array",
                tickvals=list(range(0, 1441, 60)),
                ticks="outside",
            ),
            showgrid=True,
        ),
        yaxis=dict(
            range=[-0.0125, 1.0125],
            title="Normalisierter Reisezeitvorteil",
            ticks="outside",
            showgrid=True,
        ),
    )

    async def write_image():
        async with kaleido.Kaleido(n=16, timeout=3600) as k:
            await k.write_fig(
                tuna_hist,
                path="./{}".format(file_name),
                opts=dict(format="png", scale=2, width=800, height=600),
            )

    asyncio.run(write_image())
