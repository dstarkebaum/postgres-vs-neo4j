import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dep
import plotly.graph_objs as go
import dash_table

from ..db_utils import benchmark
from ..db_utils import credentials

from . import dash_app
app = dash_app.app

tests = benchmark.tests

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
                    options=[{'label': key, 'value': key} for key in credentials.postgres],
                    value=next(iter(credentials.postgres)),
                    #style={'width': '99%'},
                ),
            ], style = {'width': '49%', 'display': 'table-cell'},
            ),
#                      ===========Test selector=============
            html.Div([

                dcc.Dropdown(
                    id='select_test',
                    #options=[{'label': '', 'value': ''}],
                    multi=False,
                    placeholder='Choose a test...',
                    options=[{'label': tests[i]['desc'], 'value': i} for i in range(len(tests))],
                    value=0,
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


#===============================Callbacks=======================================

@app.callback([
        dep.Output('results_graph','figure'),
        dep.Output('postgres_test_query','value'),
        dep.Output('neo4j_test_query','value'),
    ],[
        dep.Input('select_database_size', 'value'),
        dep.Input('select_test', 'value'),
    ],
)
def update_graph(db_size, test_number):
    postgres_results = benchmark.get_test_filename('postgres',db_size, test_number)
    neo4j_results = benchmark.get_test_filename('neo4j',db_size, test_number)
    postgres_times = []
    neo4j_times = []
    #postgres_count = 0
    #neo4j_count = 0
    with open(postgres_results, 'r') as f:
        for line in f:
            #postgres_count += 1
            postgres_times.append(float(line.strip(' "')))
    with open(neo4j_results, 'r') as f:
        for line in f:
            #neo4j_count += 1
            neo4j_times.append(float(line.strip(' "')))

    trace = [
            go.Scatter(
                    x=list(range(1,len(postgres_times)+1)), y=postgres_times,
                    name='Postgres', mode='lines',
                    marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}},
                    ),
            go.Scatter(
                    x=list(range(1,len(neo4j_times)+1)), y=neo4j_times,
                    name='Neo4j', mode='lines',
                    marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}},
                    ),
            ]

    return [{'data': trace, 'layout':go.Layout(
            title="Test results", colorway=['#fdae61', '#abd9e9', '#2c7bb6'],
            yaxis={"title": "Execution time (s)"}, xaxis={"title": "Iteration"}
            ),},

            tests[test_number]['post'].strip(),
            tests[test_number]['neo4j'].strip(),
            ]
