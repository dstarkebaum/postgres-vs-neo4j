from . import dash_app
from . import search_tab
from . import stats_tab

import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dep


#from tabs import tab_1
#from tabs import tab_2

app = dash_app.app

app.layout = html.Div([
    html.H1(
        children = 'Postgres-vs-Neo4j',
        style = {'textAlign': 'center'},
    ),
    dcc.Tabs(
        id = 'main-tab',
        children=[
            dcc.Tab(label = 'Database Stats', value = 'stats-tab'),
            dcc.Tab(label = 'Live Search', value = 'search-tab'),
        ],
        value = 'stats-tab',
    ),
    html.Div(id='main-tab-content')
])



@app.callback([
        dep.Output('main-tab-content', 'children'),
    ],[
        dep.Input('main-tab', 'value')
    ]
)
def render_content(tab):
    if tab == 'stats-tab':
        return [stats_tab.make_layout()]
    elif tab == 'search-tab':
        return [search_tab.make_layout()]

if __name__ == '__main__':
    app.run_server(debug=True)
