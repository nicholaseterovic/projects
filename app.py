import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as dhc
import dash.dependencies as ddp

import rubiks_cube.rubik as rubik

####################################################################################################

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title= 'Nick\'s Projects'
server = app.server

####################################################################################################

app.layout = dhc.Div([
    dcc.Tabs([
        dcc.Tab(
            style={'width':'10vh', 'padding':10},
            className='fas fa-cube fa-lg',
            children=[
                dcc.Store(id='rubik-store-state', data=None),
                dbc.Row(
                    no_gutters=True,
                    children=[
                        dbc.Col(
                            width=2,
                            children=[
                                dbc.Button(id='rubik-button-reset', children='reset', n_clicks=0),
                            ],
                        ),
                        dbc.Col(
                            width=10,
                            children=[
                                dcc.Graph(
                                    id='rubik-graph-state',
                                    style={'height':'90vh'},
                                    figure={},
                                    config={'scrollZoom':False, 'displayModeBar':False},
                                ),
                            ],
                        ),
                    ],
                ),   
            ],
        ),
    ]),
])

####################################################################################################

@app.callback(
    ddp.Output('rubik-store-state', 'data'),
    [
        ddp.Input('rubik-button-reset', 'n_clicks'),
        ddp.Input('rubik-graph-state', 'clickData'),
    ],
    [
        ddp.State('rubik-store-state', 'data'),
    ],
)
def set_cube_state(reset_clicks:int, clickData:dict, state:list) -> list:
    cube = rubik.RubiksCube(state=state)
    trigger = dash.callback_context.triggered[0]
    if not state or trigger['prop_id'].endswith('reset.n_clicks'):
        cube = rubik.RubiksCube(state=None)
    elif trigger['prop_id'].endswith('state.clickData'):
        if not clickData:
            return dash.no_update
        face = clickData['points'][0]['text']
        cube.rotate(operation=face)
    return cube.get_state()

@app.callback(
    [
        ddp.Output('rubik-graph-state', 'figure'),
        ddp.Output('rubik-graph-state', 'clickData'),
    ],
    [ddp.Input('rubik-store-state', 'data')],
)
def graph_cube_state(state:list) -> dict:
    if not state:
        return {}, None
    figure = rubik.RubiksCube().set_state(state).get_figure()
    figure['data'][-1].update({
        'hovertemplate' : 'Click to Rotate',
    })
    figure['layout'].update({
        'hovermode':'closest',
        'uirevision':'keep',
        'padding':{'t':0,'b':0,'l':0,'r':0},
        'showlegend':False,
    })
    return figure, None
    
####################################################################################################

if __name__ == '__main__':
    app.run_server(debug=False)