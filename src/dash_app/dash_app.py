import dash

app = dash.Dash()# __name__, external_stylesheets=external_stylesheets)
server = app.server

app.config.suppress_callback_exceptions = True
