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
    """
    Get data from db, merge with zones and add some features to be used in figures.

    :return: Data to use in figures
    :rtype: pd.DataFrame
    """
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
initial_length = len(data)


def get_loader(min_hour=0, max_hour=23, days=None):
    """
    This function generates a loading bar that shows the current data you are working with and
     its proportion to all data.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Loading bar for data used
    :rtype: dcc.Loading
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    df = data[(data['hour'].between(min_hour, max_hour)) & (data['weekday'].isin(days))]
    return dcc.Loading(
                className='loader',
                id='loading',
                type='default',
                children=[
                    dcc.Markdown(id='data_summary_filtered', children=f'{len(df):,d} taxi trips selected'),
                    html.Progress(id='selected_progress', max=f'{initial_length}', value=f'{len(df)}'),
                ])


@app.callback(
    Output('loading', 'children'),
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_loader(hours, days):
    """
    This function updates loading bar with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed loading bar
    :rtype: dcc.Loading
    """
    return get_loader(min_hour=min(hours), max_hour=max(hours), days=days)


def get_slider():
    """
    Slider to filter hours in data.

    :return: Slider filter
    :rtype: dcc.RangeSlider
    """
    return dcc.RangeSlider(
                id='hours',
                value=[0, 23],
                min=0,
                max=23,
                marks={i: str(i) for i in range(0, 24, 3)}
            )


def get_dropdown():
    """
    Dropdown list to select days to filter data.

    :return: Dropdown filter
    :rtype: dcc.Dropdown
    """
    return dcc.Dropdown(
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
                    )


def draw_sunburst_pu(min_hour=0, max_hour=23, days=None):
    """
    Sunburst chart for pick up boroughs.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Sunburst chart
    :rtype: go.Figure
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    df = data[(data['hour'].between(min_hour, max_hour)) & (data['weekday'].isin(days))]
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
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_sunburst_pu(hours, days):
    """
    This function updates sunburst chart for pick up boroughs with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed sunburst chart
    :rtype: go.Figure
    """
    return draw_sunburst_pu(min_hour=min(hours), max_hour=max(hours), days=days)


def draw_sunburst_do(min_hour=0, max_hour=23, days=None):
    """
    Sunburst chart for drop off boroughs.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Sunburst chart
    :rtype: go.Figure
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    df = data[(data['hour'].between(min_hour, max_hour)) & (data['weekday'].isin(days))]
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
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_sunburst_do(hours, days):
    """
    This function updates sunburst chart for drop off boroughs with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed sunburst chart
    :rtype: go.Figure
    """
    return draw_sunburst_do(min_hour=min(hours), max_hour=max(hours), days=days)


def draw_sankey(boro='Manhattan', min_hour=0, max_hour=23, days=None):
    """
    Return a sankey diagram that takes given pick up borough as source and every other borough except itself as drop off
     destination, and then takes each drop off borough as source to all zones of said boroughs.

    :param boro: Pick up borough to select as source
    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Sankey diagram
    :rtype: go.Figure
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    boro_filtered = data[
        (data['PUBorough'] == boro)
        & (data['DOBorough'] != boro)
        & (data['hour'].between(min_hour, max_hour))
        & (data['weekday'].isin(days))
        ]
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

    return go.Figure(
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
            )


@app.callback(
    Output('sankey-diagram', 'figure'),
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_sankey(hours, days):
    """
    This function updates sankey diagram with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed sankey diagram
    :rtype: go.Figure
    """
    return draw_sankey(min_hour=min(hours), max_hour=max(hours), days=days)


def gdraw_line1(min_hour=0, max_hour=23):
    """
    Return a line chart that shows total trip counts by pick up borough for weekdays.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :return: Line chart
    :rtype: go.Figure
    """
    df = data[(data['hour'].between(min_hour, max_hour))]
    gr = df.groupby(['PUBorough', 'weekday'])\
        .agg(trip_counts=('VendorID', 'count'))\
        .reset_index(drop=False)
    return px.line(gr, x='weekday', y='trip_counts', color='PUBorough') \
        .update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
        )


@app.callback(
    Output('gdraw-line1', 'figure'),
    Input('hours', 'value'),
)
def update_gdraw_line1(hours):
    """
    This function updates gdraw_line1's figure with callback input hours.

    :param hours: Selected hours range
    :return: Renewed line chart
    :rtype: go.Figure
    """
    return gdraw_line1(min_hour=min(hours), max_hour=max(hours))


def gdraw_line2(min_hour=0, max_hour=23):
    """
    Return a line chart that shows total trip counts by drop off borough for weekdays.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :return: Line chart
    :rtype: go.Figure
    """
    df = data[(data['hour'].between(min_hour, max_hour))]
    gr = df.groupby(['DOBorough', 'weekday'])\
        .agg(trip_counts=('VendorID', 'count'))\
        .reset_index(drop=False)
    return px.line(gr, x='weekday', y='trip_counts', color='DOBorough') \
        .update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
        )


@app.callback(
    Output('gdraw-line2', 'figure'),
    Input('hours', 'value'),
)
def update_gdraw_line2(hours):
    """
    This function updates gdraw_line2's figure with callback input hours.

    :param hours: Selected hours range
    :return: Renewed line chart
    :rtype: go.Figure
    """
    return gdraw_line2(min_hour=min(hours), max_hour=max(hours))


def draw_bar(min_hour=0, max_hour=23):
    """
    Return a bar chart that shows total amount paid for taxi rides by payment type for weekdays.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :return: Bar chart
    :rtype: go.Figure
    """
    df = data[(data['hour'].between(min_hour, max_hour))]
    pt = {
        1: 'Credit card',
        2: 'Cash',
        3: 'No charge',
        4: 'Dispute',
        5: 'Unknown',
        6: 'Voided trip',
    }
    df['payment_type'] = df['payment_type'].replace(pt)
    gr = df.groupby(['payment_type', 'weekday']) \
        .agg(total_amount=('total_amount', 'sum')) \
        .reset_index(drop=False)
    return px.bar(gr, x='weekday', y='total_amount', color='payment_type', barmode='group') \
        .update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )


@app.callback(
    Output('draw-bar', 'figure'),
    Input('hours', 'value'),
)
def update_draw_bar(hours):
    """
    This function updates bar chart figure with callback input hours.

    :param hours: Selected hours range
    :return: Renewed bar chart
    :rtype: go.Figure
    """
    return draw_bar(min_hour=min(hours), max_hour=max(hours))


def kpi_card1(min_hour=0, max_hour=23, days=None):
    """
    Return a kpi card that shows total trip count.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Kpi card
    :rtype: dbc.Card
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    df = data[(data['hour'].between(min_hour, max_hour)) & (data['weekday'].isin(days))]
    total = df['VendorID'].count().round()
    return dbc.Card(id='kpi-card1', children=[
        dbc.CardBody(
            [
                html.H4('Total Trips', className='card-title'),
                html.P(f'{int(total):,d}', className='card-value'),
            ]
        ),
    ])


@app.callback(
    Output('kpi-card1', 'children'),
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_kpi_card1(hours, days):
    """
    This function updates kpi_card1 with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed kpi_card1
    :rtype: dbc.Card
    """
    return kpi_card1(min_hour=min(hours), max_hour=max(hours), days=days)


def kpi_card2(min_hour=0, max_hour=23, days=None):
    """
    Return a kpi card that shows total trip distance.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Kpi card
    :rtype: dbc.Card
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    df = data[(data['hour'].between(min_hour, max_hour)) & (data['weekday'].isin(days))]
    total = df['trip_distance'].sum().round()
    return dbc.Card(id='kpi-card2', children=[
        dbc.CardBody(
            [
                html.H4('Total Trip Distance', className='card-title'),
                html.P(f'{int(total):,d}', className='card-value'),
            ]
        ),
    ])


@app.callback(
    Output('kpi-card2', 'children'),
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_kpi_card2(hours, days):
    """
    This function updates kpi_card2 with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed kpi_card2
    :rtype: dbc.Card
    """
    return kpi_card2(min_hour=min(hours), max_hour=max(hours), days=days)


def kpi_card3(min_hour=0, max_hour=23, days=None):
    """
    Return a kpi card that shows total amount spent for taxi rides.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Kpi card
    :rtype: dbc.Card
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    df = data[(data['hour'].between(min_hour, max_hour)) & (data['weekday'].isin(days))]
    total = df['total_amount'].sum().round()
    return dbc.Card(id='kpi-card3', children=[
        dbc.CardBody(
            [
                html.H4('Total Trip Payment Amount', className='card-title'),
                html.P(f'{int(total):,d}', className='card-value'),
            ]
        ),
    ])


@app.callback(
    Output('kpi-card3', 'children'),
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_kpi_card3(hours, days):
    """
    This function updates kpi_card3 with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed kpi_card3
    :rtype: dbc.Card
    """
    return kpi_card3(min_hour=min(hours), max_hour=max(hours), days=days)


def kpi_card4(min_hour=0, max_hour=23, days=None):
    """
    Return a kpi card that shows total passenger count.

    :param min_hour: Min hour to filter data
    :param max_hour: Max hour to filter data
    :param days: Days to filter data
    :return: Kpi card
    :rtype: dbc.Card
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    df = data[(data['hour'].between(min_hour, max_hour)) & (data['weekday'].isin(days))]
    total = df['passenger_count'].sum().round()
    return dbc.Card(id='kpi-card4', children=[
        dbc.CardBody(
            [
                html.H4('Total Passenger Amount', className='card-title'),
                html.P(f'{int(total):,d}', className='card-value'),
            ]
        ),
    ])


@app.callback(
    Output('kpi-card4', 'children'),
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_kpi_card4(hours, days):
    """
    This function updates kpi_card4 with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed kpi_card4
    :rtype: dbc.Card
    """
    return kpi_card4(min_hour=min(hours), max_hour=max(hours), days=days)


# Build App
app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div(children=[
                                    get_loader(),
                                ])
                            ])
                        )
                    ])
                ], width=2),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div(children=[
                                    html.Label('Select pick-up hours'),
                                    get_slider(),
                                    ])
                                ])
                            )
                        ])
                ], width=5),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div(children=[
                                    html.Label('Select pick-up days'),
                                    get_dropdown(),
                                    ])
                                ])
                            )
                        ])
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
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(
                                    id='sankey-diagram',
                                    figure=draw_sankey(boro='Manhattan'),
                                    config={
                                        'displayModeBar': False
                                        }
                                    )
                                ])
                            ),
                        ])
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label('Key performance indicators'),
                            kpi_card1()
                        ]),
                        dbc.Col([
                            kpi_card2()
                        ]),
                    ], align='center'),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            kpi_card3()
                        ]),
                        dbc.Col([
                            kpi_card4()
                        ]),
                    ], align='center'),
                ])
                ,
                dbc.Col([
                    html.Label('Trip counts by Pick up Borough, for weekdays'),
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(
                                    id='gdraw-line1',
                                    figure=gdraw_line1(),
                                    config={
                                        'displayModeBar': False
                                    }
                                )
                            ])
                        ),
                    ])
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label('Total amount paid by payment type'),
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(
                                id='draw-bar',
                                figure=draw_bar(),
                                config={
                                    'displayModeBar': False
                                }
                            )
                        ])
                    ),
                ], width=6),
                dbc.Col([
                    html.Label('Trip counts by Drop off Borough, for weekdays'),
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(
                                id='gdraw-line2',
                                figure=gdraw_line2(),
                                config={
                                    'displayModeBar': False
                                }
                            )
                        ])
                    ),
                ], width=6)
            ], align='center')
        ]), color='dark'
    )
])


if __name__ == '__main__':
    app.run_server(debug=config.app.debug)
