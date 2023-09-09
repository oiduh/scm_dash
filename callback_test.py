from dash import callback, Input, Output, Dash, html


app = Dash(__name__)
app.layout = html.Div([
    html.Div(id='first', children=["abc"]),
    html.Div(id='second', children=["def"]),
])

if __name__ == '__main__':
    app.run(debug=True)
