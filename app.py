import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
import plotly.express as px
import plotly.graph_objects as go
from util.config import config


app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])


def draw_sunburst():
    sun_data = dict(
        character=["Eve", "Cain", "Seth", "Enos", "Noam", "Abel", "Awan", "Enoch", "Azura"],
        parent=["", "Eve", "Eve", "Seth", "Seth", "Eve", "Eve", "Awan", "Eve"],
        value=[10, 14, 12, 10, 2, 6, 6, 4, 4]
    )
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.sunburst(
                            sun_data,
                            names='character',
                            parents='parent',
                            values='value',
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


def draw_sankey():
    with open('data/sk_data.json') as f:
        sk_data = json.load(f)

    # override gray link colors with 'source' colors
    node = sk_data['data'][0]['node']
    link = sk_data['data'][0]['link']

    # Change opacity
    node['color'] = [
        'rgba(255,0,255,{})'.format(0.8)
        if c == "magenta" else c.replace('0.8', '0.8')
        for c in node['color']]

    link['color'] = [
        node['color'][src] for src in link['source']]

    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=go.Figure(
                        go.Sankey(link=link, node=node)
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


# Text field
def draw_text():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("Place holder"),
                ], style={'textAlign': 'center'})
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
                    draw_sunburst()
                ], width=3),
                dbc.Col([
                    draw_figure()
                ], width=3),
                dbc.Col([
                    draw_sankey()
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_figure()
                ], width=9),
                dbc.Col([
                    draw_figure()
                ], width=3),
            ], align='center'),
        ]), color='dark'
    )
])


if __name__ == '__main__':
    app.run_server(debug=config.app.debug)
