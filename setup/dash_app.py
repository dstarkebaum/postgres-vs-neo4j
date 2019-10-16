import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dep
import sqlalchemy
import re
import pandas as pd
import dash_table
import sqlalchemy.dialects
import py2neo
import psycopg2
import plotly.graph_objs as obj
from setup import neo4j_utils
from setup import postgres_utils as pgu
from setup import credentials

pgu.set_database('david')


def postgres_connect(database='medium'):
    url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.url.format(
            user=credentials.postgres[database]['user'],
            password=credentials.postgres[database]['pass'],
            host=credentials.postgres[database]['host'],
            database=credentials.postgres[database]['database']
    )
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    return con

def neo4j_connect(database='medium'):
    graph = Graph(
            user=credentials.neo4j[database]['user'],
            host=credentials.neo4j[database]['host'],
            password=credentials.neo4j[database]['password']
            )
    return graph

# The dash app
app = dash.Dash()
# The flask server
server = app.server

# colors = {
#     'background': '#333333',
#     'text': '#00DD00'
# }

#graph = neo4j_connect()
#sqldb = postgres_connect()


#get_authors = '''MATCH (a:Author) return a.name'''
#authors = neo4j_utils.verbose_query(graph,get_authors)

#style={'backgroundColor': colors['background']},

app.layout = html.Div(children=[
    html.H1(
        children='Postgres-vs-Neo4j',
        style=dict(
            textAlign = 'center'
            #color = colors['text']
            )
    ),
    html.Div(
        children='Choose an author and start the queries!',
        style= dict(
            textAlign = 'center'
            ),
        #'color': colors['text']
    ),
    html.Div([
        html.Div([
            # search bar for author. debaunce=True means they have to hit enter to start
            dcc.Input(
                id='search_bar',
                placeholder='Author Name...',
                type='search',
                value='',
                size = '40',
                debounce=True,
                ),
            ], style = dict(
                    width = '20%',
                    display = 'table-cell',
                    ),
        ),
        html.Div([
            # Button for executing search (alternative to pressing enter)
            html.Button(
                children='Search',
                id='execute_search',
                type='submit',
                n_clicks=0,
                ),
            ], style = dict(
                    display = 'table-cell',
                    ),
        ),
        ], style = dict(
                width = '100%',
                display = 'table',
                ),
    ),
    html.Div([
        html.Div(
            id='author_query',
            children='',
            ),
        dcc.Dropdown(
            id='author_list',
            #options=[{'label': '', 'value': ''}],
            multi=False,
            placeholder='Authors...',
            value='',
            ),

        html.Div(
            id='author_search_time',
            children='',
            # style= dict(
            #     textAlign = 'center'
            #     ),
            ),
    ]),
    html.Div([
        html.Div(
            id='papers_query',
            children='',
            ),
        dcc.Dropdown(
            id='papers_list',
            #options=[{'label': '', 'value': ''}],
            multi=False,
            placeholder='Papers...',
            value='',
            ),
        html.Div(
            id='papers_search_time',
            children='',
            # style= dict(
            #     textAlign = 'center'
            #     ),
            ),

    ]),
])

@app.callback([
    dep.Output('author_query', 'children'),
    dep.Output('author_list', 'options'),
    dep.Output('author_search_time', 'children'),
    ],
    [dep.Input('search_bar', 'value')],
)
def update_author_list(search_string):

    # only allow alphanumeric inputs
    pattern = re.compile("[A-Za-z0-9]+")
    if pattern.fullmatch(search_string) is not None:
        query = '''
            SELECT name, id FROM authors WHERE name ILIKE '%{name}%' LIMIT 20
        '''.format(name=search_string)

        r = pgu.return_query(query)
        return [
            query,
            [{'label':name,'value':str(id)} for (name,id) in r['results']],
            "{:1.2f} ms".format(r['time']*1000),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            '',
            [{'label':'Use only A-Z,a-z,0-9 for author names','value':''}],
            "0.0 ms",
            ]

@app.callback([
    dep.Output('papers_query', 'children'),
    dep.Output('papers_list', 'options'),
    dep.Output('papers_search_time', 'children'),
    ],
    [dep.Input('author_list', 'value')],
)
def update_papers_list(author_id):

    # only allow alphanumeric inputs
    if author_id is not '':
        #print("Found match: " + string)
        query='''
            SELECT papers.title, papers.id FROM papers, (
                select paper_id from has_author
                where has_author.author_id = {author_id}
            ) as z
            where papers.id = z.paper_id;
            '''.format(
                author_id=author_id
                )
        r = pgu.return_query(query)
        return [
            query,
            [{'label':name,'value':str(id)} for (name,id) in r['results']],
            "{:1.2f} ms".format(r['time']*1000),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            '',
            [{'label':'Use only A-Z,a-z,0-9 for author names','value':''}],
            "0.0 ms",
            ]


if __name__ == '__main__':
    app.run_server(debug=True)






# dcc.Graph(
#     id='Graph1',
#     figure={
#         'data': [
#             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
#             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
#         ],
#         'layout': {
#             'plot_bgcolor': colors['background'],
#             'paper_bgcolor': colors['background'],
#             'font': {
#                 'color': colors['text']
#             }
#         }
#     }
# )
