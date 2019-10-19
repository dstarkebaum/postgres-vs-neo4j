import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dep
import dash_table

from . import dash_app
app = dash_app.app


def make_layout():
    return html.Div(children=[

        dcc.Graph(
            id='Graph1',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                #'layout': {
                    #'plot_bgcolor': colors['background'],
                    #'paper_bgcolor': colors['background'],
                    #'font': {
                    #    'color': colors['text']
                    #}
                #}
            }
        )
    ]) # end layout
