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
merged['lpep_pickup_datetime'] = pd.to_datetime(merged['lpep_pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
merged['lpep_dropoff_datetime'] = pd.to_datetime(merged['lpep_dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')
merged['weekday'] = merged['lpep_pickup_datetime'].apply(lambda x: x.weekday())
merged['trip_time'] = (merged['lpep_dropoff_datetime'] - merged['lpep_pickup_datetime'])
merged['trip_time'] = merged['trip_time'].apply(lambda x: round(x.seconds / 60))


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
                                color='rgba(255, 0, 255, 0.65)',
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
                )
            ])
        ),
    ])


# Data
df = px.data.iris()


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


def gdraw_line(x='weekday', y='value', group=None):
    if group is None:
        group = ['PUBorough', 'weekday']
    color = group[0]

    gr = merged.groupby(group)\
        .agg(value=('VendorID', 'count'))\
        .reset_index(drop=False)
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.line(
                        gr,
                        x=x,
                        y=y,
                        color=color
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


def kpi_card(col='trip_distance'):
    total = merged[col].sum().round()
    return dbc.Card([
        dbc.CardBody(
            [
                html.H4(f'Total {col}', className='card-title'),
                html.P(total, className='card-value'),
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


# Build App
app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    get_loader()
                ], width=2),
                dbc.Col([
                    get_slider()
                ], width=5),
                dbc.Col([
                    get_dropdown()
                ], width=5),
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
                    html.Label('Sankey chart for Drop offs from Manhattan to other Boroughs'),
                    draw_sankey(boro='Manhattan')
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        html.H4('Total Trips', className='card-title'),
                                        html.P(merged['VendorID'].count().round(), className='card-value'),
                                    ]
                                ),
                            ])
                        ]),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        html.H4('Total Trip Distance', className='card-title'),
                                        html.P(merged['trip_distance'].sum().round(), className='card-value'),
                                    ]
                                ),
                            ])
                        ]),
                    ], align='center'),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        html.H4('Total Trip Payment Amount', className='card-title'),
                                        html.P(merged['total_amount'].sum().round(), className='card-value'),
                                    ]
                                ),
                            ])
                        ]),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        html.H4('Total Passenger Amount', className='card-title'),
                                        html.P(merged['passenger_count'].sum().round(), className='card-value'),
                                    ]
                                ),
                            ])
                        ]),
                    ], align='center'),
                ])
                ,
                dbc.Col([
                    html.Label('Trip counts by Pick up Borough, for weekdays'),
                    gdraw_line(group=['PUBorough', 'weekday'])
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_figure()
                ], width=4),
                dbc.Col([
                    html.Label('Trip counts by Drop off Borough, for weekdays'),
                    gdraw_line(group=['DOBorough', 'weekday'])
                ], width=8)
            ], align='center')
        ]), color='dark'
    )
])


if __name__ == '__main__':
    app.run_server(debug=config.app.debug)
