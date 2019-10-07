import dash
import dash_core_components as dcc
import dash_html_components as html
import sqlalchemy
import pandas as pd
import dash_table
import sqlalchemy.dialects
import py2oneo
import psycopg2
import plotly.graph_objs as go


def postgres_connect():
    user = 'ubuntu'
    password = 'ubuntu'
    db = 'ubuntu'
    host = '10.0.0.6'
    url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.url.format(
            user=user,password=password,host=host,database=database
    )
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    return con

def noo4j_connect():
    user = 'neo4j'
    password = 'insight'
    db = 'neo4j'
    host = '10.0.0.6'
    graph = Graph(host="10.0.0.11",password="password")
    url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.url.format(
            user=user,password=password,host=host,database=database
    )
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    return con


postgres = postgres_connect()




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
