import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dep
import plotly.graph_objs as go
import dash_table
import os

from ..db_utils import benchmark
from ..db_utils import credentials

from . import dash_app
app = dash_app.app

tests = benchmark.tests
db_sizes = {
    'local':'200 papers',
    'small':'11 million papers',
    'medium':'51 million papers',
    'large':'176 million papers',
    }

def make_layout():
    return html.Div(children=[
#                      ===========Database selector=============
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id='select_database_size',
                    #options=[{'label': '', 'value': ''}],
                    multi=False,
                    placeholder='Database Size...',
                    options=[{'label': key + ": "+db_sizes[key], 'value': key} for key in credentials.postgres],
                    value=next(iter(credentials.postgres)),
                    #style={'width': '99%'},
                ),
            ], style = {'width': '49%', 'display': 'table-cell'},
            ),
#                      ===========Test selector=============
            html.Div([

                dcc.Dropdown(
                    id='warm_or_cold',
                    #options=[{'label': '', 'value': ''}],
                    multi=False,
                    placeholder='Warm or cold...',
                    options=[
                            {'label':'Warm','value':'warm'},
                            {'label':'Cold','value':'cold'}
                            ],
                    #options=[{'label': tests[i]['desc'], 'value': i} for i in range(len(tests))],
                    value='warm',
                    #style={'width': '99%'},
                ),
            ], style = {'width': '49%', 'display': 'table-cell'}
            ),
        ], style = {'width': '100%', 'display': 'table'},
        ),

        #html.Div([
            # Button for executing search (alternative to pressing enter)
        #    html.Button(
        #        children='Re-run Test',
        #        id='run_test',
        #        type='submit',
        #        n_clicks=0,
        #    ),
        #]),
#                      ===========Results graph=============
        dcc.Graph(
            id='results_graph',
            style={"height" : "30%", "width" : "100%"},
            #figure={
            #    'data': [{},{}],
                #'layout': {
                    #'plot_bgcolor': colors['background'],
                    #'paper_bgcolor': colors['background'],
                    #'font': {
                    #    'color': colors['text']
                    #}
                #}
            #},
        ),
#                      ===========Queries=============
        html.Div([

            dcc.Dropdown(
                id='select_test',
                #options=[{'label': '', 'value': ''}],
                multi=False,
                placeholder='View a test query...',
                options=[{'label': str(i+1)+': '+tests[i]['desc'], 'value': i} for i in range(len(tests))],
                value=0,
                #style={'width': '99%'},
            ),
        ], #style = {'width': '49%', 'display': 'table-cell'}
        ),


        html.Div([
#                      ===========Postgres=============
            html.Div([
                html.Div(children='Postgres Query:'),
                dcc.Textarea(
                        id='postgres_test_query',
                        style={'width': '98%'},
                        placeholder='Postgres Query...',
                        rows=8,
                    ),
            ], style = {'width': '49%', 'display': 'table-cell'},
            ),
#                      ===========Neo4j=============
            html.Div([
                html.Div(children='Neo4j Query:'),
                dcc.Textarea(
                        id='neo4j_test_query',
                        style={'width': '98%'},
                        placeholder='Neo4j Query...',
                        rows=8,
                    )
                ], style = {'width': '49%', 'display': 'table-cell'}
                ),
        ], style = {'width': '100%', 'display': 'table'},
        ),
    ]) # end layout


def read_test_results(database, db_size,warm_or_cold):

    results = list(range(len(benchmark.tests)))
    num_tests = len(benchmark.tests)
    for i in range(num_tests):
        test_filename = benchmark.get_test_filename(database,db_size, i)

        #if os.path.exists(test_filename):

        try:
            with open(test_filename, 'r') as f:
                count = 0
                for line in f:
                    if 0 == count and 'cold' == warm_or_cold:
                        #take only the first test result as 'cold'
                        results[i] = float(line.strip(' "'))

                    if 'warm' == warm_or_cold:
                        # keep overwriting so you end up with just the last result
                        results[i] = float(line.strip(' "'))
                    count +=1
        except IOError as e:
            results[i]=0
    return results
#===============================Callbacks=======================================

@app.callback([
        dep.Output('results_graph','figure'),
        #dep.Output('postgres_test_query','value'),
        #dep.Output('neo4j_test_query','value'),
    ],[
        dep.Input('select_database_size', 'value'),
        dep.Input('warm_or_cold', 'value'),
    ],
)
def update_graph(db_size, warm_or_cold):
    postgres_times = read_test_results('postgres',db_size,warm_or_cold)
    neo4j_times = read_test_results('neo4j',db_size,warm_or_cold)
    #postgres_count = 0
    #neo4j_count = 0

    trace = [
            go.Bar(
                    x=list(range(1,len(postgres_times)+1)), y=postgres_times,
                    name='Postgres',# mode='lines',
                    #marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}},
                    hovertext = [str(i)+': '+tests[i]['desc'] for i in range(len(tests))],
                    hoverinfo = 'text'
                    ),
            go.Bar(
                    x=list(range(1,len(neo4j_times)+1)), y=neo4j_times,
                    name='Neo4j',# mode='lines',
                    #marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}},
                    hoverinfo='skip'
                    ),
            ]

    return [{'data': trace, 'layout':go.Layout(
            title="Postgres-vs-Neo4j", colorway=['#fdae61', '#abd9e9', '#2c7bb6'],
            yaxis={"title": "Execution time (s)"}, xaxis={"title": "Test Number"}
            ),},

            ]
@app.callback([
        dep.Output('postgres_test_query','value'),
        dep.Output('neo4j_test_query','value'),
    ],[
        dep.Input('select_test', 'value'),
    ],
)
def update_graph(test_number):
    return [
            tests[test_number]['post'].strip(),
            tests[test_number]['neo4j'].strip(),
    ]
