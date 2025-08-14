import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


def figures(df, additionals):
    df_mam, delta_tuna, delta_tuna_stats = additionals

    pio.templates.default = "plotly_white"

    quantiles = [0.25, 0.5, 0.75, 0.9, 0.99, 1]
    quantile_index = [
        math.floor(len(df.index) * 0.25),
        math.floor(len(df.index) * 0.5),
        math.floor(len(df.index) * 0.75),
        math.floor(len(df.index) * 0.9),
        math.floor(len(df.index) * 0.99),
    ]
    quantile_text = ["25%", "50%", "75%", "90%", "99%"]

    scatter_symbols = ["diamond", "square", "circle", "triangle-up", "x"]

    relative_keys = [
        "Offset-Routing %",
        "1. Verfügbarkeitsprüfung %",
        "ÖV-Routing %",
        "2. Verfügbarkeitsprüfung %",
        "Mixing %",
    ]

    def walltime_stacked_bar():
        df.sort_values(by="Gesamtzeit", ignore_index=True, inplace=True)
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

    def walltime_violin():
        violin_keys = [
            "Gesamtzeit",
            "Offset-Routing",
            "1. Verfügbarkeitsprüfung",
            "ÖV-Routing",
            "2. Verfügbarkeitsprüfung",
            "Mixing",
        ]
        violins = go.Figure()
        for k in violin_keys:
            df.sort_values(by=k, ignore_index=True, inplace=True)
            print("{} quantiles:".format(k))
            print(df[k].quantile(quantiles))
            violins.add_trace(
                go.Violin(y=df[k], name=k, box_visible=True, meanline_visible=True)
            )
        violins.update_layout(yaxis_title="Wall-Time [ms]", showlegend=False)
        violins.show()

    def absolute_section_time_scatter():
        absolute_keys = [
            "Offset-Routing",
            "1. Verfügbarkeitsprüfung",
            "ÖV-Routing",
            "2. Verfügbarkeitsprüfung",
            "Mixing",
        ]
        df.sort_values(by="Gesamtzeit", ignore_index=True, inplace=True)
        scatter_absolute = go.Figure()
        for k, s in zip(absolute_keys, scatter_symbols):
            scatter_absolute.add_trace(
                go.Scatter(
                    name=k,
                    mode="markers",
                    x=df["Gesamtzeit"],
                    y=df[k],
                    marker=dict(symbol=s),
                )
            )
        scatter_absolute.update_layout(
            font=dict(family="Arial", size=14),
            yaxis_title="Zeit in Abschnitt [ms]",
            xaxis_title="Gesamte Wall-Time [ms]",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )
        scatter_absolute.show()

    def relative_section_time_scatter():
        scatter_relative = go.Figure()
        for k, s in zip(relative_keys, scatter_symbols):
            scatter_relative.add_trace(
                go.Scatter(
                    name=k,
                    mode="markers",
                    x=df["Gesamtzeit"],
                    y=df[k],
                    marker=dict(symbol=s),
                )
            )
        scatter_relative.update_layout(
            yaxis_title="Anteil in %",
            xaxis_title="Gesamte Wall-Time [ms]",
            legend=dict(yanchor="top", y=0.5, xanchor="right", x=0.99),
        )
        scatter_relative.show()

    def taxi_rides_per_section_violin():
        violin_taxis = make_subplots(rows=1, cols=2)
        violin_taxis.add_trace(
            go.Violin(
                y=df["n_taxis_init"],
                name="Initial",
                box_visible=True,
                meanline_visible=True,
            ),
            row=1,
            col=1,
        )
        violin_taxis.add_trace(
            go.Violin(
                y=df["n_taxis_blacklist"],
                name="1. Verfügbark.",
                box_visible=True,
                meanline_visible=True,
            ),
            row=1,
            col=1,
        )
        violin_taxis.add_trace(
            go.Violin(
                y=df["n_taxis_routing"],
                name="Routing",
                box_visible=True,
                meanline_visible=True,
            ),
            row=1,
            col=2,
        )
        violin_taxis.add_trace(
            go.Violin(
                y=df["n_taxis_whitelist"],
                name="2. Verfügbark.",
                box_visible=True,
                meanline_visible=True,
            ),
            row=1,
            col=2,
        )
        violin_taxis.update_layout(yaxis_title="Anzahl Taxifahrten", showlegend=False)
        violin_taxis.show()

    def walltime_per_taxi_ride():
        violin_per_taxi = make_subplots(rows=1, cols=2)
        violin_per_taxi.add_trace(
            go.Violin(
                y=df["bl_per_taxi"],
                name="1. Verfügbarkeitsprüfung",
                box_visible=True,
                meanline_visible=True,
            ),
            row=1,
            col=1,
        )
        violin_per_taxi.add_trace(
            go.Violin(
                y=df["wl_per_taxi"],
                name="2. Verfügbarkeitsprüfung",
                box_visible=True,
                meanline_visible=True,
            ),
            row=1,
            col=2,
        )
        violin_per_taxi.update_layout(
            yaxis_title="Zeit pro angefragtem Taxi [ms]", showlegend=False
        )
        violin_per_taxi.show()

    def mam_fig():
        mam_fig = px.bar(df_mam, y=["pt", "pt_by_taxi"])
        mam_fig.update_layout(
            bargap=0,
            xaxis_title="Tageszeit",
            xaxis_tickmode="array",
            xaxis_tickvals=list(range(0, 1440, 60)),
            xaxis_ticktext=["{:02d}:00".format(x // 60) for x in range(0, 1440, 60)],
            xaxis_ticks="outside",
            yaxis_title="Anzahl Verbindungen",
            yaxis_dtick=1000,
            legend=dict(
                traceorder="reversed", yanchor="top", y=0.99, xanchor="left", x=0.01
            ),
        )
        mam_fig.show()

    def tuna_fig():
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

        tuna_hist = go.Figure(
            go.Histogram2d(
                x=x,
                y=y,
                autobinx=False,
                xbins=dict(start=0, end=1440, size=10),
                autobiny=False,
                ybins=dict(start=0, end=1.01, size=0.01),
                colorscale="greys",
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
        tuna_hist.update_layout(
            xaxis_range=[0, 1440],
            xaxis_title="Tageszeit",
            xaxis_tickmode="array",
            xaxis_tickvals=list(range(0, 1441, 120)),
            yaxis_range=[0, 1.01],
            xaxis_ticktext=["{:02d}:00".format(x // 60) for x in range(0, 1441, 120)],
            xaxis_ticks="outside",
            yaxis_title="Normalisierter Reisezeitvorteil",
            showlegend=True,
        )
        tuna_hist.show()

    # walltime_stacked_bar()
    # walltime_violin()
    # absolute_section_time_scatter()
    # relative_section_time_scatter()
    # taxi_rides_per_section_violin()
    # walltime_per_taxi_ride()
    # mam_fig()
    tuna_fig()
