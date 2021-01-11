import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
from util.config import config


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


# Data
df = px.data.iris()

# Build App
app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    draw_text()
                ], width=3),
                dbc.Col([
                    draw_text()
                ], width=3),
                dbc.Col([
                    draw_text()
                ], width=3),
                dbc.Col([
                    draw_text()
                ], width=3),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_figure()
                ], width=3),
                dbc.Col([
                    draw_figure()
                ], width=3),
                dbc.Col([
                    draw_figure()
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
