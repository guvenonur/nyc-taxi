import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from util.config import config


app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])

df2 = pd.read_csv('data/green_tripdata_2019-03.csv')
zones = pd.read_csv('data/zones.csv')


def get_main_data():
    zones.columns = ['PULocationID', 'PUBorough', 'PUZone', 'PUservice_zone']
    merged = df2.merge(zones, how='left', on='PULocationID')
    zones.columns = ['DOLocationID', 'DOBorough', 'DOZone', 'DOservice_zone']
    merged = merged.merge(zones, how='left', on='DOLocationID')
    merged['lpep_pickup_datetime'] = pd.to_datetime(merged['lpep_pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
    merged['lpep_dropoff_datetime'] = pd.to_datetime(merged['lpep_dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')
    merged['weekday'] = merged['lpep_pickup_datetime'].apply(lambda x: x.weekday())
    merged['hour'] = merged['lpep_pickup_datetime'].apply(lambda x: x.hour)
    merged['trip_time'] = (merged['lpep_dropoff_datetime'] - merged['lpep_pickup_datetime'])
    merged['trip_time'] = merged['trip_time'].apply(lambda x: round(x.seconds / 60))
    return merged


data = get_main_data()


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
                            dcc.Markdown(id='data_summary_filtered', children=f'Hello loading {len(data)}'),
                            html.Progress(id="selected_progress", max=f"{len(data)}", value=f"{len(data) - 20}"),
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
                        min=0,
                        max=23,
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


def draw_sunburst_pu(min_hour=0, max_hour=23, min_day=0, max_day=6):
    df = data[(data['hour'].between(min_hour, max_hour))
              & (data['weekday'].between(min_day, max_day))]
    gp = df.groupby(['PUBorough', 'PUZone']) \
        .agg(value=('VendorID', 'count')) \
        .reset_index(drop=False)

    return px.sunburst(gp, path=['PUBorough', 'PUZone'], values='value') \
        .update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )


@app.callback(
    Output('sunburst-pu', 'figure'),
    Input('hours', 'value')
)
def update_sunburst_pu(value, min_day=0, max_day=6):
    return draw_sunburst_pu(min_hour=min(value), max_hour=max(value), min_day=min_day, max_day=max_day)


def draw_sunburst_do(min_hour=0, max_hour=23, min_day=0, max_day=6):
    df = data[(data['hour'].between(min_hour, max_hour))
              & (data['weekday'].between(min_day, max_day))]
    gp = df.groupby(['DOBorough', 'DOZone']) \
        .agg(value=('VendorID', 'count')) \
        .reset_index(drop=False)

    return px.sunburst(gp, path=['DOBorough', 'DOZone'], values='value') \
        .update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )


@app.callback(
    Output('sunburst-do', 'figure'),
    Input('hours', 'value')
)
def update_sunburst_do(value, min_day=0, max_day=6):
    return draw_sunburst_do(min_hour=min(value), max_hour=max(value), min_day=min_day, max_day=max_day)


def draw_sankey(boro):
    boro_filtered = data[(data['PUBorough'] == boro) & (data['DOBorough'] != boro)]
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


def gdraw_line(x='weekday', y='value', group=None):
    if group is None:
        group = ['PUBorough', 'weekday']
    color = group[0]

    gr = data.groupby(group)\
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


def kpi_card1(min_val=0, max_val=23, col='trip_distance'):
    merged2 = data[data['hour'].between(min_val, max_val)]
    total = merged2[col].sum().round()
    return dbc.Card(id='kpi-card', children=[
        dbc.CardBody(
            [
                html.H4('Total Trips', className='card-title'),
                html.P(f'{min_val}, {max_val}', className='card-value2'),
                html.P(total, className='card-value'),
            ]
        ),
    ])


@app.callback(
    Output('kpi-card', 'children'),
    Input('hours', 'value')
)
def update_kpi_card(value):
    return kpi_card1(min_val=min(value), max_val=max(value), col='trip_distance')


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
                    html.Div(children=[
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(
                                    id='sunburst-pu',
                                    figure=draw_sunburst_pu(),
                                    config={
                                        'displayModeBar': False
                                    }
                                )
                            ])
                        ),
                    ])
                ], width=3),
                dbc.Col([
                    html.Label('Sun burst chart for Drop offs'),
                    html.Div(children=[
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(
                                    id='sunburst-do',
                                    figure=draw_sunburst_do(),
                                    config={
                                        'displayModeBar': False
                                    }
                                 )
                                ])
                            ),
                        ])
                ], width=3),
                dbc.Col([
                    html.Label('Sankey diagram for Drop offs from Manhattan to other Boroughs'),
                    draw_sankey(boro='Manhattan')
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            kpi_card1()
                        ]),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        html.H4('Total Trip Distance', className='card-title'),
                                        html.P(data['trip_distance'].sum().round(), className='card-value'),
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
                                        html.P(data['total_amount'].sum().round(), className='card-value'),
                                    ]
                                ),
                            ])
                        ]),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        html.H4('Total Passenger Amount', className='card-title'),
                                        html.P(data['passenger_count'].sum().round(), className='card-value'),
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
                    gdraw_line(group=['PUBorough', 'weekday'])
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
