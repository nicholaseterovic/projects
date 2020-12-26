# Nicholas Eterovic 2020Q4
####################################################################################################

# Open-source Dash packages.
import dash
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as dhc
import dash_trich_components as dtc
import dash_bootstrap_components as dbc

# Open-source miscellanous packages.
import typing as tp

# In-house packages.
import util.system as su
from rubiks_cube.rubik import RubiksCube

####################################################################################################
# APPLICATION

app = dash.Dash(
    name=__name__,
    title='Nicholas Eterovic',
    prevent_initial_callbacks=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.0/css/all.css',
    ],
)
server = app.server

####################################################################################################
# LAYOUT

projects = {
    'cube':{'label':'Rubik\'s Cube', 'icon':'fas fa-cube'},
}

links = {
    'github':{'icon':'fab fa-github', 'href':'https://github.com/NicholasEterovic'},
    'linkedin':{'icon':'fab fa-linkedin', 'href':'https://www.linkedin.com/in/nicholaseterovic'},
    'instagram':{'icon':'fab fa-instagram', 'href':'https://www.instagram.com/nicholaseterovic'},
}

empty_figure = {
    'layout':{
        'xaxis':{'visible':False},
        'yaxis':{'visible':False},
        'annotations':[
            {
                'text':'Select a Cube Size and Load',
                'xref':'paper',
                'yref':'paper',
                'showarrow':False,
                'font':{'size':30},
            },
        ],
    },
}

app.layout = dhc.Div(style={'position':'relative', 'height':'100vh'}, children=[
    dtc.SideBar(bg_color='#2f4f4f', children=[
        dhc.Hr(),
        dtc.SideBarItem(label='PROJECTS'),
        *[
            dtc.SideBarItem(id=f'sbi-{project}', icon=kwargs['icon'], label=kwargs['label'])
            for project, kwargs in projects.items()
        ],
        dhc.Hr(),
        dtc.SideBarItem(label='LINKS'),
        *[
            dhc.Div(style={'margin-left':'20px'}, children=[
                dcc.Link(
                    target='_blank',
                    href=kwargs['href'],
                    style={'margin-left':'20px'},
                    children=[dtc.SideBarItem(icon=kwargs['icon'], label='')],
                ),
            ])
            for link, kwargs in links.items()
        ],
        dhc.Hr(),
    ]),
    dhc.Div(id='page_content', children=[
        dcc.Tabs(
            id='tabs-projects',
            value=list(projects)[0],
            style={'height':'0px'},
            children=[
                dcc.Tab(
                    value='cube',
                    style={'overflow-y':'scroll'},
                    children=[
                        dcc.Store(id='rubik-store-state', data=None),
                        dbc.InputGroup(
                            size='sm',
                            children=[
                                dbc.InputGroupAddon(addon_type='append', children=[
                                    dbc.Button(
                                        id='rubik-button-load',
                                        children='Load',
                                        n_clicks=0,
                                        color='primary',
                                        disabled=False,
                                    ),
                                ]),
                                dbc.Select(
                                    id='rubik-select-dim',
                                    value=3,
                                    options=[
                                        {'label':f'{n}x{n} Cube', 'value':n}
                                        for n in range(1, 6)
                                    ],
                                ),
                                dbc.InputGroupAddon(addon_type='prepend', children=[
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
                            style={'height':'100vh', 'border':'1px black solid'},
                            config={'scrollZoom':True, 'displayModeBar':True, 'displaylogo':False},
                            figure=empty_figure,
                        ),
                    ],
                ),
            ],
        ),
    ]),
])

####################################################################################################
# NAVIGATION

@app.callback(
    ddp.Output('tabs-projects', 'value'),
    [ddp.Input(f'sbi-{project}', 'n_clicks') for project in projects],
)
def click_tab(*_:tp.List[int]) -> str:
    trigger = dash.callback_context.triggered[0]
    return trigger['prop_id'].replace('sbi-', '').replace('.n_clicks', '')

####################################################################################################
# RUBIKS CUBE

@app.callback(
    ddp.Output('rubik-store-state', 'data'),
    [
        ddp.Input('rubik-button-load', 'n_clicks'),
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
    cube = RubiksCube(dim=int(dim), state=state)
    trigger = dash.callback_context.triggered[0]
    if not trigger['value'] or trigger['prop_id'].endswith('load.n_clicks'):
        cube = RubiksCube(dim=int(dim), state=None)
    elif trigger['prop_id'].endswith('scramble.n_clicks'):
        cube.scramble()
    elif trigger['prop_id'].endswith('state.clickData'):
        faces, axes = zip(*RubiksCube._face_axes.items())
        point = trigger['value']['points'][0]
        coord = {axis:point[axis] for axis in ['x', 'y', 'z']}
        axis = max(coord.keys(), key=lambda axis:abs(coord[axis]))
        axis += '+' if coord[axis]>0 else '-'
        face = list(faces)[list(axes).index(axis)]
        cube.rotate(operation=face)
    return cube.get_state()
    
@app.callback(
    [
        ddp.Output('rubik-graph-state', 'figure'),
        ddp.Output('rubik-graph-state', 'clickData'),
    ],
    [ddp.Input('rubik-store-state', 'data')],
    [ddp.State('rubik-select-dim', 'value'),]
)
def graph_cube_state(state:list, dim:int) -> dict:
    if not state:
        return empty_figure, None
    figure = RubiksCube(dim=int(dim), state=state).get_figure()
    for trace in figure['data']:
        trace.update({
            'hoverinfo':'none' if trace['type']=='mesh3d' else 'skip',
            'hovertemplate':'',
            'name':None,
        })
    figure['layout'].update({
        'margin':{'t':0,'b':0,'l':0,'r':0, 'pad':0},
        'uirevision':'keep',
        'showlegend':False,
    })
    return figure, None

@app.callback(
    ddp.Output('rubik-button-scramble', 'disabled'),
    [
        ddp.Input('rubik-select-dim', 'value'),
        ddp.Input('rubik-graph-state', 'figure'),
    ],
)
def enable_scramble_button(dim:int, figure:dict) -> bool:
    trigger = dash.callback_context.triggered[0]
    if trigger['prop_id'].endswith('dim.value'):
        return True
    return not trigger['value']

####################################################################################################
# DEPLOY

if __name__ == '__main__':
    kwargs = su.get_cli_kwargs()
    app.run_server(**kwargs)