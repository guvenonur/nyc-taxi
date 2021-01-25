import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from db.operations import Operations


app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])

zones = pd.read_csv('data/zones.csv')
op = Operations
data = op.get_main_data(zones=zones)
initial_length = len(data)


def get_loader(df=data):
    """
    This function generates a loading bar that shows the current data you are working with and
     its proportion to all data.

    :param df: Initial data
    :return: Loading bar for data used
    :rtype: dcc.Loading
    """
    return dcc.Loading(
                className='loader',
                id='loading',
                type='default',
                children=[
                    dcc.Markdown(id='data_summary_filtered', children=f'{len(df):,d} taxi trips selected'),
                    html.Progress(id='selected_progress', max=f'{initial_length}', value=f'{len(df)}'),
                ])


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


def draw_sunburst_pu(df=data):
    """
    Sunburst chart for pick up boroughs.

    :param df: Initial data
    :return: Sunburst chart
    :rtype: go.Figure
    """
    gp = df.groupby(['PUBorough', 'PUZone']) \
        .agg(value=('VendorID', 'count')) \
        .reset_index(drop=False)

    return px.sunburst(gp, path=['PUBorough', 'PUZone'], values='value') \
        .update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )


def draw_sunburst_do(df=data):
    """
    Sunburst chart for drop off boroughs.

    :param df: Initial data
    :return: Sunburst chart
    :rtype: go.Figure
    """
    gp = df.groupby(['DOBorough', 'DOZone']) \
        .agg(value=('VendorID', 'count')) \
        .reset_index(drop=False)

    return px.sunburst(gp, path=['DOBorough', 'DOZone'], values='value') \
        .update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )


def draw_sankey(boro='Manhattan', df=data):
    """
    Return a sankey diagram that takes given pick up borough as source and every other borough except itself as drop off
     destination, and then takes each drop off borough as source to all zones of said boroughs.

    :param boro: Pick up borough to select as source
    :param df: Initial data
    :return: Sankey diagram
    :rtype: go.Figure
    """
    boro_filtered = df[
        (df['PUBorough'] == boro)
        & (df['DOBorough'] != boro)
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
                        line = dict(
                            width=0.5,
                            color='rgba(255, 0, 255, 0.65)'
                        ),
                        label=[''] + list(zones['DOZone']) + list(zd.keys())
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


def gdraw_line1(df=data):
    """
    Return a line chart that shows total trip counts by pick up borough for weekdays.

    :param df: Initial data
    :return: Line chart
    :rtype: go.Figure
    """
    gr = df.groupby(['PUBorough', 'weekday'])\
        .agg(trip_counts=('VendorID', 'count'))\
        .reset_index(drop=False)
    return px.line(gr, x='weekday', y='trip_counts', color='PUBorough')\
        .update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
        )


def gdraw_line2(df=data):
    """
    Return a line chart that shows total trip counts by drop off borough for weekdays.

    :param df: Initial data
    :return: Line chart
    :rtype: go.Figure
    """
    gr = df.groupby(['DOBorough', 'weekday'])\
        .agg(trip_counts=('VendorID', 'count'))\
        .reset_index(drop=False)
    return px.line(gr, x='weekday', y='trip_counts', color='DOBorough')\
        .update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
        )


def draw_bar(df=data):
    """
    Return a bar chart that shows total amount paid for taxi rides by payment type for weekdays.

    :param df: Initial data
    :return: Bar chart
    :rtype: go.Figure
    """
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


def kpi_card1(df=data):
    """
    Return a kpi card that shows total trip count.

    :param df: Data to calculate kpi
    :return: Kpi card
    :rtype: dbc.Card
    """
    total = len(df)
    return [
        html.H4('Total Trips', className='card-title'),
        html.P(f'{int(total):,d}', className='card-value'),
    ]


def kpi_card2(df=data):
    """
    Return a kpi card that shows total trip distance.

    :param df: Data to calculate kpi
    :return: Kpi card
    :rtype: dbc.Card
    """
    total = df['trip_distance'].sum().round()
    return [
        html.H4('Total Trip Distance', className='card-title'),
        html.P(f'{int(total):,d}', className='card-value'),
    ]


def kpi_card3(df=data):
    """
    Return a kpi card that shows total amount spent for taxi rides.

    :param df: Data to calculate kpi
    :return: Kpi card
    :rtype: dbc.Card
    """
    total = df['total_amount'].sum().round()
    return [
        html.H4('Total Trip Payment Amount', className='card-title'),
        html.P(f'{int(total):,d}', className='card-value'),
    ]


def kpi_card4(df=data):
    """
    Return a kpi card that shows total passenger count.

    :param df: Data to calculate kpi
    :return: Kpi card
    :rtype: dbc.Card
    """
    total = df['passenger_count'].sum().round()
    return [
        html.H4('Total Passenger Amount', className='card-title'),
        html.P(f'{int(total):,d}', className='card-value'),
    ]


@app.callback(
    Output('loading', 'children'),
    Output('sunburst-pu', 'figure'),
    Output('sunburst-do', 'figure'),
    Output('sankey-diagram', 'figure'),
    Output('gdraw-line1', 'figure'),
    Output('gdraw-line2', 'figure'),
    Output('draw-bar', 'figure'),
    Output('kpi-card1', 'children'),
    Output('kpi-card2', 'children'),
    Output('kpi-card3', 'children'),
    Output('kpi-card4', 'children'),
    Input('hours', 'value'),
    Input('days', 'value'),
)
def update_all(hours, days):
    """
    This function updates all components(charts, diagram and kpi cards) with callback inputs hours and days.

    :param hours: Selected hours range
    :param days: Selected days
    :return: Renewed components
    :rtype: dbc.Card, dcc.Loading, go.Figure
    """
    if days is None or len(days) == 0:
        days = [0, 1, 2, 3, 4, 5, 6]
    new_data_h = data[data['hour'].between(min(hours), max(hours))]
    new_data = new_data_h[new_data_h['weekday'].isin(days)]

    return get_loader(df=new_data),\
        draw_sunburst_pu(df=new_data),\
        draw_sunburst_do(df=new_data),\
        draw_sankey(df=new_data), \
        gdraw_line1(df=new_data_h),\
        gdraw_line2(df=new_data_h),\
        draw_bar(df=new_data_h),\
        kpi_card1(df=new_data),\
        kpi_card2(df=new_data),\
        kpi_card3(df=new_data),\
        kpi_card4(df=new_data)


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
                            dbc.Card(id='kpi-card1', children=[
                                dbc.CardBody(
                                    kpi_card1()
                                    ),
                                ])
                        ]),
                        dbc.Col([
                            dbc.Card(id='kpi-card2', children=[
                                dbc.CardBody(
                                    kpi_card2()
                                    ),
                                ])
                        ]),
                    ], align='center'),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card(id='kpi-card3', children=[
                                dbc.CardBody(
                                    kpi_card3()
                                    ),
                                ])
                        ]),
                        dbc.Col([
                            dbc.Card(id='kpi-card4', children=[
                                dbc.CardBody(
                                    kpi_card4()
                                        ),
                                    ])
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
    app.run_server(debug=False, use_reloader=False)
