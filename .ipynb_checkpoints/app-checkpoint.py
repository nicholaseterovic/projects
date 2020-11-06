import dash
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as dhc
import dash_bootstrap_components as dbc

import typing as tp

import rubiks_cube.rubik as rubik

####################################################################################################

app = dash.Dash(
    name=__name__,
    title='Nicholas Eterovic',
    prevent_initial_callbacks=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
    ],
)
server = app.server

####################################################################################################

tabs = {
    'cube':{'label':'Rubiks Cube'},
}

app.layout = dhc.Div([
    dbc.NavbarSimple(
        brand='Nicholas Eterovic',
        brand_href='http://www.nicholaseterovic.com/',
        color='dark',
        dark=True,
        fluid=True,
        children=[
            dbc.DropdownMenu(
                id='dropdownmenuitem-projects',
                label='Projects',
                nav=True,
                in_navbar=True,
                children=[
                    dbc.DropdownMenuItem(
                        id=f'dropdownmenuitem-project-{tab}',
                        children=kwargs['label'],
                    )
                    for tab, kwargs in tabs.items()
                ],
            ),
            dbc.NavItem([
                dbc.ButtonGroup([
                    dbc.Button(
                        className='fas fa-github-square',
                        color='link',
                        href='https://github.com/NicholasEterovic',
                    ),
                    dbc.Button(
                        className='fas fa-linkedin-square',
                        color='link',
                        href='https://www.linkedin.com/in/nicholaseterovic',
                    ),
                    dbc.Button(
                        className='fas fa-instagram-square',
                        color='link',
                        href='https://www.instagram.com/nicholaseterovic/',
                    ),
                ]),
            ]),
        ],
    ),
    dcc.Tabs(
        id='tabs-projects',
        value='tab-'+list(tabs)[0],
        style={'height':'0px'},
        children=[
            dcc.Tab(
                value='tab-cube',
                children=[
                    dcc.Store(id='rubik-store-state', data=None),
                    dbc.InputGroup(
                        children=[
                            dbc.InputGroupAddon([
                                dbc.Button(
                                    id='rubik-button-reset',
                                    children='Reset',
                                    n_clicks=0,
                                    color='primary',
                                    disabled=False,
                                ),
                            ]),
                            dbc.Select(
                                id='rubik-select-dim',
                                value=3,
                                options=[{'label':f'{n}x{n} Cube', 'value':n} for n in range(1, 11)],
                                disabled=True,
                            ),
                            dbc.InputGroupAddon([
                                dbc.Button(
                                    id='rubik-button-scramble',
                                    children='Scramble',
                                    n_clicks=0,
                                    color='warning',
                                    disabled=True,
                                ),
                            ]),
                        ],
                    ),
                    dcc.Graph(
                        id='rubik-graph-state',
                        style={'height':'90vh', 'border':'1px black solid'},
                        config={'scrollZoom':True, 'displayModeBar':False},
                        figure={},
                    ),
                ],
            ),
        ],
    ),
])

####################################################################################################
# NAVIGATION

@app.callback(
    ddp.Output('tabs-projects', 'value'),
    [ddp.Input(f'dropdownmenuitem-project-{tab}', 'n_clicks') for tab in tabs],
)
def click_project_tab(*args:list) -> str:
    trigger = dash.callback_context.triggered[0]
    return 'tab-'+trigger['prop_id'].rsplit('.', maxsplit=1)[0].rsplit('-', maxsplit=1)[-1]
        
####################################################################################################
# RUBIKS CUBE

@app.callback(
    ddp.Output('rubik-store-state', 'data'),
    [
        ddp.Input('rubik-button-reset', 'n_clicks'),
        ddp.Input('rubik-button-scramble', 'n_clicks'),
        ddp.Input('rubik-graph-state', 'clickData'),
    ],
    [
        ddp.State('rubik-select-dim', 'value'),
        ddp.State('rubik-store-state', 'data'),
    ],
)
def set_cube_state(*args:list) -> tp.List[dict]:
    *_, dim, state = args
    cube = rubik.RubiksCube(state=state)
    trigger = dash.callback_context.triggered[0]
    if not trigger['value'] or trigger['prop_id'].endswith('reset.n_clicks'):
        cube = rubik.RubiksCube(dim=int(dim), state=None)
    elif trigger['prop_id'].endswith('scramble.n_clicks'):
        cube.scramble()
    elif trigger['prop_id'].endswith('state.clickData'):
        face = trigger['value']['points'][0]['text']
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
    figure['data'][-1].update({'hovertemplate' : 'Click to Rotate'})
    figure['layout'].update({
        'hovermode':'closest',
        'uirevision':'keep',
        'margin':{'t':0,'b':0,'l':0,'r':0, 'pad':0},
        'showlegend':False,
    })
    return figure, None

@app.callback(
    ddp.Output('rubik-button-scramble', 'disabled'),
    [ddp.Input('rubik-graph-state', 'figure')],
)
def enable_scramble_button(figure:dict) -> bool:
    return not figure

####################################################################################################
# DEPLOY

if __name__ == '__main__':
    app.run_server(debug=False)