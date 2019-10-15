import dash
import dash_core_components as dcc
import dash_html_components as html
import sqlalchemy
import pandas as pd
import dash_table
import sqlalchemy.dialects
import py2neo
import psycopg2
import plotly.graph_objs as go
from setup import neo4j_utils
from setup import postgres_utils
from setup import credentials



def postgres_connect(database='int'):
    user = credentials.postgres[database]['user'],
    password = credentials.postgres[database]['password'])
    db = credentials.postgres[database]['database'],
    host = credentials.postgres[database]['host'],
    url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.url.format(
            user=user,password=password,host=host,database=database
    )
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    return con

def neo4j_connect(database='medium'):
    user = credentials.neo4j[database]['user'],
    password = credentials.neo4j[database]['password'])
    host = credentials.neo4j[database]['host'],
    graph = Graph(user=user,host=host,password=password)
    return graph

# The dash app
app = dash.Dash()
# The flask server
server = app.server

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
