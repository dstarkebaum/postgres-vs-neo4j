import dash
import dash_core_components as dcc
import dash_html_components as html
import sqlalchemy
import pandas as pd
import dash_table
from sqlalchemy.dialects import postgresql
import numpy as np
import plotly.graph_objs as go


def database_connect():
    user = 'ubuntu'
    password = 'ubuntu'
    db = 'ubuntu'
    host = '10.0.0.6'
    url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.url.format(
            user=user,password=password,host=host,port=port,database=database
    )
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    return con

con = database_connect()




app = dash.Dash()

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Graph(
        id='Graph1',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
