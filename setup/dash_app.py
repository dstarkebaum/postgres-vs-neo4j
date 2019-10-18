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
from setup import neo4j_utils as n4u
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

def readable_time(seconds):
    if abs(seconds) < 1:
        return "{:1.2f} ms".format(seconds*1000)
    elif abs(seconds) < 60:
        return "{:1.2f} sec".format(seconds)
    elif abs(seconds) < 3600:
        return "{:1.2f} min".format(seconds / 60)
    elif abs(seconds) < 86400:
        return "{:1.2f} hr".format(seconds / 3600)
    else:
        return "{:1.2f} day".format(seconds / 86400)


def query_box(id,placeholder):
    return dcc.Textarea(
        id=id,
        placeholder=placeholder,
        style={'width': '98%'},
        rows=4,
    )

def dropdown_menu(id, placeholder, value=''):
    return dcc.Dropdown(
        id=id,
        placeholder=placeholder,
        #options=[{'label': '', 'value': ''}],
        multi=False,
        value=value,
        style={'width': '99%'},
        )


# The dash app
app = dash.Dash()
# The flask server
server = app.server

# colors = {
#     'background': '#333333',
#     'text': '#00DD00'
# }

graph = n4u.start_connection('medium-remote')
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

#===============================Set Database====================================
    html.Div([
#                      ===========Postgres=============
        html.Div([

            dcc.Dropdown(
                id='postgres_set_database',
                #options=[{'label': '', 'value': ''}],
                multi=False,
                placeholder='Postgres Database...',
                options=[{'label': key, 'value': key} for key in credentials.postgres],
                style={'width': '99%'},
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),
    #                      ===========Neo4j=============
        html.Div([
            dcc.Dropdown(
                id='neo4j_set_database',
                #options=[{'label': '', 'value': ''}],
                multi=False,
                placeholder='Neo4j Database...',
                options=[{'label': key, 'value': key} for key in credentials.neo4j],
                style={'width': '99%'},
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),

        ], style = dict(
            width = '100%',
            display = 'table',
            )
    ),
    html.Div([
#===============================Count Database==================================
#                      ===========Postgres=============
        html.Div([
            html.Div(
                children='Postres Papers: ',
                ),
            html.Div(
                id='postgres_papers_count',
                children='',
                ),
            html.Div(
                children='Authors: ',
                ),
            html.Div(
                id='postgres_authors_count',
                children='',
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),
    #                      ===========Neo4j=============
        html.Div([
            html.Div(
                children='Neo4j Papers: ',
                ),
            html.Div(
                id='neo4j_papers_count',
                children='',
                ),
            html.Div(
                children='Authors: ',
                ),
            html.Div(
                id='neo4j_authors_count',
                children='',
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),

        ], style = dict(
            width = '100%',
            display = 'table',
            )
    ),

#=================================Search Bar====================================
    html.Div([
#                      ===========Postgres=============
        html.Div([
            html.Div(
                children='Postgres:',
                #style= dict(
                #    textAlign = 'center'
                #    ),
                ),
            # search bar for author. debaunce=True means they have to hit enter to start
            dcc.Input(
                id='postgres_search_bar',
                placeholder='Author Name...',
                type='search',
                value='',
                size = '40',
                debounce=True,
                ),
            # Button for executing search (alternative to pressing enter)
            html.Button(
                children='Search',
                id='postgres_execute_search',
                type='submit',
                n_clicks=0,
                ),
            html.Div(
                id='postgres_author_search_time',
                children='',
                style = {'display':'inline-block','textAlign':'center'}
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
        ),
#                      ===========Neo4j=============
        html.Div([
            html.Div(
                children='Neo4j:',
                #style= dict(
                #    textAlign = 'center'
                #    ),
                ),
            # search bar for author. debaunce=True means they have to hit enter to start
            dcc.Input(
                id='neo4j_search_bar',
                placeholder='Author Name...',
                type='search',
                value='',
                size = '40',
                debounce=True,
                ),
            # Button for executing search (alternative to pressing enter)
            html.Button(
                children='Search',
                id='neo4j_execute_search',
                type='submit',
                n_clicks=0,
                ),
            html.Div(
                id='neo4j_author_search_time',
                children='',
                style = {'display':'inline-block','textAlign':'center'}
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
        ),

        ], style = {'width': '100%', 'display': 'table'}
    ),

#===============================Author Dropdown=================================
    html.Div([
#                      ===========Postgres=============
        html.Div([
            query_box(
                id='postgres_author_query',
                placeholder='Postgres author query...',
            ),

            dropdown_menu(
                id='postgres_author_list',
                placeholder='Authors...',
                ),
            html.Div(
                id='postgres_papers_search_time',
                children='',
                style = {'display':'inline-block','textAlign':'center'}
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),

    #                      ===========Neo4j=============
        html.Div([
            query_box(
                id='neo4j_author_query',
                placeholder='Neo4j author query...',
            ),
            dropdown_menu(
                id='neo4j_author_list',
                placeholder='Authors...',
                ),
            html.Div(
                id='neo4j_papers_search_time',
                children='',
                style = {'display':'inline-block','textAlign':'center'}
                ),

            ], style = {'width': '49%', 'display': 'table-cell'}
            ),

        ], style = dict(
            width = '100%',
            display = 'table',
            )
    ),


#===============================Papers dropdown=================================
    html.Div([
#                      ===========Postgres=============
        html.Div([
            query_box(
                id='postgres_papers_query',
                placeholder='Postgres paper query...',
            ),
            dropdown_menu(
                id='postgres_papers_list',
                placeholder='Papers...',
                ),
            html.Div(
                id='postgres_cites_search_time',
                children='',
                style = {'display':'inline-block','textAlign':'center'}
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),
    #                      ===========Neo4j=============
        html.Div([
            query_box(
                id='neo4j_papers_query',
                placeholder='Neo4j paper query...',
            ),
            dropdown_menu(
                id='neo4j_papers_list',
                placeholder='Papers...',
                ),
            html.Div(
                id='neo4j_cites_search_time',
                children='',
                style = {'display':'inline-block','textAlign':'center'}
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),

        ], style = {'width': '100%', 'display': 'table'}
    ),

#===============================Cites dropdown=================================
    html.Div([
#                      ===========Postgres=============
        html.Div([
            query_box(
                id='postgres_cites_query',
                placeholder='Postgres cites query...',
            ),
            dropdown_menu(
                id='postgres_cites_list',
                placeholder='Cites...',
                ),

            ], style = {'width': '49%', 'display': 'table-cell'}
            ),
    #                      ===========Neo4j=============
        html.Div([
            query_box(
                id='neo4j_cites_query',
                placeholder='Neo4j cites query...',
            ),
            dropdown_menu(
                id='neo4j_cites_list',
                placeholder='Cites...',
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),

        ], style = {'width': '100%', 'display': 'table'}
    ),

]) # end app layout


#===============================Callbacks=======================================

#===============================Set Database====================================
#                      ===========Postgres=============
@app.callback([
    dep.Output('postgres_papers_count','children'),
    dep.Output('postgres_authors_count','children'),
    ],
    [dep.Input('postgres_set_database', 'value')],)
def set_postgres_database(database):

    if database in credentials.postgres:
        pgu.set_database(database)
        query_papers = "SELECT count(*) FROM papers;"
        query_authors = "SELECT count(*) FROM authors;"

        num_papers = pgu.return_query(query_papers)['results'][0][0]
        num_authors = pgu.return_query(query_authors)['results'][0][0]
        return [num_papers,num_authors]
    else:
        return [0,0]

#                      ===========Neo4j=============
@app.callback([
    dep.Output('neo4j_papers_count','children'),
    dep.Output('neo4j_authors_count','children'),
    ],
[dep.Input('neo4j_set_database', 'value')],)
def set_neo4j_database(database):

    # only allow alphanumeric inputs
    if database in credentials.neo4j:
        global graph
        graph = n4u.start_connection(database)
        query_papers = "MATCH (p:Paper) RETURN count(p);"
        query_authors = "MATCH (a:Author) RETURN count(a);"

        num_papers = n4u.return_query(graph,query_papers)['results'][0][0]
        num_authors = n4u.return_query(graph,query_authors)['results'][0][0]
        return [num_papers,num_authors]
    else:
        return [0,0]

#===============================Author search===================================
#                      ===========Postgres=============
@app.callback([
    dep.Output('postgres_author_query', 'value'),
    dep.Output('postgres_author_list', 'options'),
    dep.Output('postgres_author_search_time', 'children'),
    ],
    [dep.Input('postgres_search_bar', 'value')],
)
def update_postgres_author_list(search_string):
    # only allow alphanumeric inputs
    pattern = re.compile("[A-Za-z0-9]+")
    if pattern.fullmatch(search_string) is not None:
        query = '''
            SELECT name, id FROM authors WHERE name ILIKE '%{name}%' LIMIT 20;
        '''.format(name=search_string)

        r = pgu.return_query(query)
        return [
            query.strip(),
            [{'label':name,'value':str(id)} for (name,id) in r['results']],
            readable_time(r['time']),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            'Use only A-Z,a-z,0-9 for author names',
            [{'label':'','value':''}],
            "0.0 ms",
            ]

#                      ===========Neo4j=============
@app.callback([
    dep.Output('neo4j_author_query', 'value'),
    dep.Output('neo4j_author_list', 'options'),
    dep.Output('neo4j_author_search_time', 'children'),
    ],
    [dep.Input('neo4j_search_bar', 'value')],
)
def update_neo4j_author_list(search_string):
    # only allow alphanumeric inputs
    pattern = re.compile("[A-Za-z0-9]+")
    if pattern.fullmatch(search_string) is not None:
        query = '''
            MATCH (a:Author) WHERE a.name =~ '(?i).*{name}.*' RETURN a.name, a.id LIMIT 20;
        '''.format(name=search_string)

        r = n4u.return_query(graph,query)
        return [
            query.strip(),
            [{'label':name,'value':str(id)} for (name,id) in r['results']],
            readable_time(r['time']),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            'Use only A-Z,a-z,0-9 for author names',
            [{'label':'','value':''}],
            "0.0 ms",
            ]


#===============================Paper search====================================
#                      ===========Postgres=============
@app.callback([
    dep.Output('postgres_papers_query', 'value'),
    dep.Output('postgres_papers_list', 'options'),
    dep.Output('postgres_papers_search_time', 'children'),
    ],
    [dep.Input('postgres_author_list', 'value')],
)
def update_postgres_papers_list(author_id):

    # only allow alphanumeric inputs
    if author_id is not '':
        #print("Found match: " + string)
        query='''
            SELECT papers.title, papers.id FROM papers, (
                select paper_id from has_author
                where has_author.author_id = {author_id}
            ) as by_author
            where papers.id = by_author.paper_id;
            '''.format(
                author_id=author_id
                )
        r = pgu.return_query(query)
        return [
            query.strip(),
            [{'label':title,'value':str(id)} for (title,id) in r['results']],
            readable_time(r['time']),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            '',
            [{'label':'Select an author to search Postgres','value':''}],
            "0.0 ms",
            ]

#                      ===========Neo4j=============
@app.callback([
    dep.Output('neo4j_papers_query', 'value'),
    dep.Output('neo4j_papers_list', 'options'),
    dep.Output('neo4j_papers_search_time', 'children'),
    ],
    [dep.Input('neo4j_author_list', 'value')],
)
def update_neo4j_papers_list(author_id):

    # only allow alphanumeric inputs
    if author_id is not '':
        #print("Found match: " + string)
        query='''
            MATCH (p:Paper)-[:HAS_AUTHOR]->(a:Author)
            WHERE a.id = "{author_id}" RETURN p.title, p.id;
            '''.format(
                author_id=author_id
                )
        r = n4u.return_query(graph,query)
        return [
            query.strip(),
            [{'label':title,'value':str(id)} for (title,id) in r['results']],
            readable_time(r['time']),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            '',
            [{'label':'Select an author to search Neo4j','value':''}],
            "0.0 ms",
            ]

#===============================Cites search====================================
#                      ===========Postgres=============
@app.callback([
    dep.Output('postgres_cites_query', 'value'),
    dep.Output('postgres_cites_list', 'options'),
    dep.Output('postgres_cites_search_time', 'children'),
    ],
    [dep.Input('postgres_papers_list', 'value')],
)
def update_postgres_cites_list(paper_id):

    # only allow alphanumeric inputs
    if paper_id is not '':
        #print("Found match: " + string)
        query='''
            SELECT papers.title, papers.id FROM papers, (
                select incit_id from is_cited_by
                where is_cited_by.id = {target_id}
            ) as citations
            where papers.id = citations.incit_id;
            '''.format(target_id=paper_id)
        r = pgu.return_query(query)
        return [
            query.strip(),
            [{'label':title,'value':str(id)} for (title,id) in r['results']],
            readable_time(r['time']),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            '',
            [{'label':'Select a paper to search Postgres','value':''}],
            "0.0 ms",
            ]

#                      ===========Neo4j=============
@app.callback([
    dep.Output('neo4j_cites_query', 'value'),
    dep.Output('neo4j_cites_list', 'options'),
    dep.Output('neo4j_cites_search_time', 'children'),
    ],
    [dep.Input('neo4j_papers_list', 'value')],
)
def update_neo4j_cites_list(paper_id):

    # only allow alphanumeric inputs
    if paper_id is not '':
        #print("Found match: " + string)
        query='''
            MATCH (p1:Paper)-[:CITES]->(p2:Paper)
            WHERE p2.id = "{target_id}" RETURN p1.title,p1.id;
            '''.format(target_id=paper_id)

        r = n4u.return_query(graph,query)
        return [
            query.strip(),
            [{'label':title,'value':str(id)} for (title,id) in r['results']],
            readable_time(r['time']),
            ]
    else:
        # if not found match
        #print("No match")
        return [
            '',
            [{'label':'Select a paper to search Neo4j','value':''}],
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
