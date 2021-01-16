import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from util.config import config


app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])
df2 = pd.read_csv('data/green_tripdata_2019-03.csv')
zones = pd.read_csv('data/zones.csv')

zones.columns = ['PULocationID', 'PUBorough', 'PUZone', 'PUservice_zone']
merged = df2.merge(zones, how='left', on='PULocationID')
zones.columns = ['DOLocationID', 'DOBorough', 'DOZone', 'DOservice_zone']
merged = merged.merge(zones, how='left', on='DOLocationID')


def draw_sunburst(path):
    gp = merged.groupby(path) \
        .agg(value=('VendorID', 'count')) \
        .reset_index(drop=False)
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.sunburst(
                        gp,
                        path=path,
                        values='value'
                        ).update_layout(
                            template='plotly_dark',
                            plot_bgcolor='rgba(0, 0, 0, 0)',
                            paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ])


def draw_sankey(boro):
    boro_filtered = merged[(merged['PUBorough'] == boro) & (merged['DOBorough'] != boro)]
    sk = boro_filtered \
        .groupby(['PUBorough', 'DOBorough']) \
        .agg(value=('VendorID', 'count')) \
        .reset_index(drop=False)
    zd = {
        'EWR': 266,
        'Queens': 267,
        'Bronx': 268,
        'Manhattan': 269,
        'Staten Island': 270,
        'Brooklyn': 271,
        'Unknown': 272
    }
    sk['PUBorough'] = sk['PUBorough'].replace(zd)
    sk['DOBorough'] = sk['DOBorough'].replace(zd)

    sk2 = boro_filtered \
        .groupby(['DOBorough', 'DOZone']) \
        .agg(value=('VendorID', 'count')) \
        .reset_index(drop=False)
    zd2 = zones.set_index('DOZone')['DOLocationID'].to_dict()
    sk2['DOBorough'] = sk2['DOBorough'].replace(zd)
    sk2['DOZone'] = sk2['DOZone'].replace(zd2)
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=go.Figure(
                        data=[go.Sankey(
                            node=dict(
                                pad=15,
                                thickness=20,
                                label=[''] + list(zones['DOZone']) + list(zd.keys()),
                                color="blue"
                            ),
                            link=dict(
                                source=list(sk.T.loc['PUBorough', :]) + list(sk2.T.loc['DOBorough', :]),
                                target=list(sk.T.loc['DOBorough', :]) + list(sk2.T.loc['DOZone', :]),
                                value=list(sk.T.loc['value', :]) + list(sk2.T.loc['value', :])
                            )
                        )]
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                ),
                html.P("Opacity"),
                dcc.Slider(id='opacity', min=0, max=1, value=0.5, step=0.1)
            ])
        ),
    ])


# Iris bar figure
def draw_figure():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.bar(
                        df, x="sepal_width", y="sepal_length", color="species"
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ])


def get_loader():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div(className="four columns pretty_container", children=[
                    dcc.Loading(
                        className="loader",
                        id="loading",
                        type="default",
                        children=[
                            html.Div(id='loader-trigger-1', style={"display": "none"}),
                            html.Div(id='loader-trigger-2', style={"display": "none"}),
                            html.Div(id='loader-trigger-3', style={"display": "none"}),
                            html.Div(id='loader-trigger-4', style={"display": "none"}),
                            dcc.Markdown(id='data_summary_filtered', children=f'Hello loading {len(df)}'),
                            html.Progress(id="selected_progress", max=f"{len(df)}", value=f"{len(df) - 20}"),
                        ]),
                ])
            ])
        )
    ])


def get_slider():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div(className="four columns pretty_container", children=[
                    html.Label('Select pick-up hours'),
                    dcc.RangeSlider(
                        id='hours',
                        value=[0, 23],
                        min=0, max=23,
                        marks={i: str(i) for i in range(0, 24, 3)}
                    ),
                ])
            ])
        )
    ])


def get_dropdown():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div(className="four columns pretty_container", children=[
                    html.Label('Select pick-up days'),
                    dcc.Dropdown(
                        id='days',
                        placeholder='Select a day of week',
                        options=[
                            {'label': 'Monday', 'value': 0},
                            {'label': 'Tuesday', 'value': 1},
                            {'label': 'Wednesday', 'value': 2},
                            {'label': 'Thursday', 'value': 3},
                            {'label': 'Friday', 'value': 4},
                            {'label': 'Saturday', 'value': 5},
                            {'label': 'Sunday', 'value': 6}
                        ],
                        value=[],
                        multi=True
                    ),
                ])
            ])
        )
    ])


def kpi_cards():
    return dbc.Card([
        dbc.CardBody(
            [
                html.H4("Card title", className="card-title"),
                html.P(
                    "$10.5 M",
                    className="card-value",
                ),
                html.P(
                    "Target: $10.0 M",
                    className="card-target",
                ),
                html.Span(
                    "Up ",
                    className="card-diff-up",
                ),
                html.Span(
                    "5.5% vs Last Year",
                    className="card-diff-up",
                ),

            ]
        ),
    ])


# Data
df = px.data.iris()

# Build App
app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    get_loader()
                ], width=4),
                dbc.Col([
                    get_slider()
                ], width=4),
                dbc.Col([
                    get_dropdown()
                ], width=4),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label('Sun burst chart for Pick ups'),
                    draw_sunburst(path=['PUBorough', 'PUZone'])
                ], width=3),
                dbc.Col([
                    html.Label('Sun burst chart for Drop offs'),
                    draw_sunburst(path=['DOBorough', 'DOZone'])
                ], width=3),
                dbc.Col([
                    draw_sankey(boro='Manhattan')
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_figure()
                ], width=4),
                dbc.Col([
                    draw_figure()
                ], width=8),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_figure()
                ], width=4),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            kpi_cards()
                        ]),
                        dbc.Col([
                            kpi_cards()
                        ]),
                        dbc.Col([
                            kpi_cards()
                        ]),
                    ], align='center'),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            kpi_cards()
                        ]),
                        dbc.Col([
                            kpi_cards()
                        ]),
                        dbc.Col([
                            kpi_cards()
                        ]),
                    ], align='center')
                ])
            ], align='center')
        ]), color='dark'
    )
])


if __name__ == '__main__':
    app.run_server(debug=config.app.debug)
