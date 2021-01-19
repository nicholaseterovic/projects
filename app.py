# Nicholas Eterovic 2020Q4
####################################################################################################

# Open-source Dash packages.
import dash
import dash_canvas as dcv
import dash_tabulator as dtb
import dash_pivottable as dpv
import dash.exceptions as dxc
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as dhc
import dash_trich_components as dtc
import dash_bootstrap_components as dbc
import dash_extensions.javascript as djs

# Open-source miscellanous packages.
import json
import numpy as np
import pandas as pd
import typing as tp
import plotly.data as ptd
import sklearn.utils as sku
import sklearn.datasets as skd

# In-house packages.
import util.system as su
from fractal.fractal import Fractal
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
ns = djs.Namespace('dapp', 'tabulator')

####################################################################################################
# LAYOUT

projects = {
    'home':{'label':'Home', 'icon':'fas fa-home'},
    'cube':{'label':'Rubik\'s Cube', 'icon':'fas fa-cube'},
    'pivot':{'label':'Pivot Table', 'icon':'fas fa-border-all'},
    'fractal':{'label':'Fractal Generator', 'icon':'fas fa-snowflake'},
}

links = {
    'github':{'icon':'fab fa-github', 'href':'https://github.com/NicholasEterovic'},
    'linkedin':{'icon':'fab fa-linkedin', 'href':'https://www.linkedin.com/in/nicholaseterovic'},
    'instagram':{'icon':'fab fa-instagram', 'href':'https://www.instagram.com/nicholaseterovic'},
}

base_figure = {
    'layout':{
        'uirevision':'keep',
        'margin':{'t':0,'b':0,'l':0,'r':0, 'pad':0},
        'xaxis':{'visible':False},
        'yaxis':{'visible':False},
        'showlegend':False,
        'annotations':[
            {
                'text':'<b>Select a Cube Size and Load</b>',
                'xref':'paper',
                'yref':'paper',
                'x':0.5,
                'y':0.5,
                'showarrow':False,
                'font':{'size':30},
            },
            *[
                {'text':text, 'xref':'paper', 'yref':'paper', 'x':x, 'y':y, 'showarrow':False}
                for x, y, text in [
                    (0.1, 0.9, '<b>Left-click on a cube face</b><br>to rotate by 90º clockwise'),
                    (0.9, 0.9, '<b>Mouse-wheel</b><br>to zoom in and out'),
                    (0.1, 0.1, '<b>Left-click and drag</b><br>(outside the cube)<br>to rotate the cube'),
                    (0.9, 0.1, '<b>Right-click and drag</b><br>(outside the cube)<br>to reposition the cube'),
                ]
            ],
        ],
    },
}

empty_figure = {
    'data':[],
    'layout':{
        'scene':{'aspectmode':'data'},
        'hovermode':'closest',
        'margin':{'t':0,'b':0,'l':0,'r':0, 'pad':0},
        'xaxis':{'visible':False},
        'yaxis':{'visible':False},
        'showlegend':True,
        'annotations':[],
    },
}

empty_path_figure = {
    'layout':{
        **empty_figure['layout'],
        'annotations':[{
            'text':'<b>Draw</b> a piece-wise linear path<br>and <b>click</b> "Confirm"',
            'xref':'paper',
            'yref':'paper',
            'x':0.5,
            'y':0.5,
            'showarrow':False,
            'font':{'size':15},
        }],
    },
}

datasets = {
    'sklearn':{
        source:[func for func in dir(skd) if func.startswith(source)]
        for source in ['load', 'fetch', 'make']
    },
    'plotly':{
        'load':[func for func in dir(ptd) if not func.startswith('_')],
    },
}

app.layout = dhc.Div(style={'position':'relative'}, children=[
    dtc.SideBar(bg_color='#2f4f4f', children=[
        dhc.Hr(),
        *[
            dtc.SideBarItem(id=f'sbi-{project}', icon=kwargs['icon'], label=kwargs['label'])
            for project, kwargs in projects.items()
        ],
        dhc.Hr(),
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
    dhc.Div(id='page_content', style={'min-height':'100vh'}, children=[
        dcc.Tabs(
            id='tabs-projects',
            value=list(projects)[0],
            style={'height':'0px'},
            children=[
                dcc.Tab(
                    value='home',
                    style={'line-height':'0px'},
                    children=[
                        dbc.Row(
                            no_gutters=True,
                            style={'height':'100vh', 'background-color':'#2f4f4f'},
                            children=[
                                dbc.Col(width=7, children=[
                                    dbc.Jumbotron(fluid=True, style={'height':'100%'}, children=[
                                        dbc.Container(fluid=True, children=[
                                            dhc.Hr(),
                                            dhc.H3('Greetings!'),
                                            dhc.Br(),
                                            dhc.P(
                                                'You\'ve stumbled on my humble personal website, '
                                                'home to some of my recreational math and coding projects. '
                                                'Feel free to take a look at what\'s available using the sidebar. '
                                                'For the best user experience, I recommend browsing with desktop Chrome.'
                                            ),
                                            dhc.Br(),
                                            dcc.Markdown('*- Nick Eterovic*', style={'text-align':'right'}),
                                            dhc.Hr(),
                                        ]),
                                    ]),
                                ]),
                                dbc.Col(width=5, children=[
                                    dhc.Img(
                                        src='assets/profile.jpg',
                                        title='Boston, Fall of 2020',
                                        style={'max-width':'100%', 'max-height':'100vh'},
                                    ),
                                ]),
                            ],
                        ),
                    ],
                ),
                dcc.Tab(
                    value='cube',
                    style={'line-height':'0px'},
                    children=[
                        dcc.Store(id='rubik-store-state', data=None),
                        dbc.Row(no_gutters=True, children=[
                            dbc.Col(width=10, children=[
                                dbc.InputGroup(
                                    size='sm',
                                    children=[
                                        dbc.InputGroupAddon(addon_type='append', children=[
                                            dbc.Button(
                                                id='rubik-button-clear',
                                                children='Clear',
                                                n_clicks=0,
                                                color='primary',
                                                disabled=False,
                                            ),
                                        ]),
                                        dbc.InputGroupAddon(addon_type='append', children=[
                                            dbc.Button(
                                                id='rubik-button-load',
                                                children='Load',
                                                n_clicks=0,
                                                color='warning',
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
                                        dbc.Select(
                                            id='rubik-select-scramble',
                                            value=10,
                                            options=[
                                                {'label':f'{n} moves', 'value':n}
                                                for n in [5, 10, 20, 30, 50, 100]
                                            ],
                                        ),
                                    ],
                                ),
                                dcc.Graph(
                                    id='rubik-graph-state',
                                    style={'height':'calc(100vh - 31px)', 'border':'1px black solid'},
                                    config={'scrollZoom':True, 'displayModeBar':True, 'displaylogo':False},
                                    figure=base_figure,
                                ),
                            ]),
                            dbc.Col(width=2, children=[
                                dtb.DashTabulator(
                                    id='rubik-table-history',
                                    data=[],
                                    columns=[{
                                        'title':'Move History',
                                        'field':'move',
                                        'hozAlign':'center',
                                        'headerSort':False,
                                        'headerSortStartingDir':'desc',
                                    }],
                                    options={
                                        'placeholder':'None',
                                        'layout':'fitDataStretch',
                                        'height':'100vh',
                                        'minHeight':'100vh',
                                        'maxHeight':'100vh',
                                        'selectable':'false',
                                    },
                                ),
                            ]),
                        ]),
                    ],
                ),
                dcc.Tab(
                    value='pivot',
                    style={'line-height':'0px'},
                    children=[
                        dbc.InputGroup(
                            size='sm',
                            children=[
                                dbc.DropdownMenu(
                                    label='Load Data',
                                    color='primary',
                                    direction='right',
                                    addon_type='append',
                                    children=[
                                        dbc.DropdownMenuItem(
                                            children='Upload',
                                            n_clicks=0,
                                            disabled=True,
                                        ),
                                    ] + [
                                        dbc.DropdownMenu(
                                            label=library.capitalize(),
                                            direction='right',
                                            color='link',
                                            disabled=(library=='sklearn'),
                                            children=[
                                                dbc.DropdownMenu(
                                                    label=source.capitalize(),
                                                    direction='right',
                                                    color='link',
                                                    children=[
                                                        dbc.DropdownMenuItem(
                                                            id=f'pivot-dmi-{library}-{source}-{func}',
                                                            children=func.split('_', maxsplit=1)[-1],
                                                            disabled=(source=='fetch'),
                                                            n_clicks=0,
                                                        )
                                                        for func in funcs
                                                    ],
                                                )
                                                for source, funcs in sources.items()
                                            ],
                                        )
                                        for library, sources in datasets.items()
                                    ],
                                ),
                                dbc.Input(
                                    type='text',
                                    disabled=True,
                                ),
                            ],
                        ),
                        dtb.DashTabulator(
                            id='pivot-tabulator-raw',
                            data=[],
                            columns=[{
                                'title':'',
                                'field':'none',
                                'hozAlign':'center',
                                'headerSort':False,
                            }],
                            options={
                                'placeholder':'None',
                                'layout':'fitDataStretch',
                                'layoutColumnsOnNewData':False,
                                'minHeigh':'50vh',
                                'maxHeight':'50vh',
                                'height':'50vh',
                                'pagination':'local',
                                'selectable':False,
                            },
                        ),
                        dhc.Div(id='pivot-div-agg', children=[]),
                    ],
                ),
                dcc.Tab(
                    value='fractal',
                    style={'line-height':'0px'},
                    children=[
                        dbc.Row(no_gutters=True, children=[
                            dbc.Col(width=6, children=[
                                dbc.Card(style={'height':'50vh'}, children=[
                                    dbc.DropdownMenu(
                                        id=f'fractal-ddm-{comp}',
                                        label=f'Fractal {comp.capitalize()}',
                                        color='link',
                                        direction='right',
                                        children=[

                                        ],
                                    ),
                                    dbc.Row(no_gutters=True, children=[
                                        dbc.Col(width=6, children=[
                                            dcv.DashCanvas(
                                                id=f'fractal-canvas-{comp}',
                                                width=1000,
                                                height=1000,
                                                tool='line',
                                                goButtonTitle='Confirm',
                                                hide_buttons=[
                                                    'zoom',
                                                    'pan',
                                                    'pencil',
                                                    'rectangle',
                                                    'select',
                                                ]
                                            ),
                                        ]),
                                        dbc.Col(width=6, children=[
                                            dcc.Graph(
                                                id=f'fractal-graph-{comp}',
                                                style={'height':'100%'},
                                                figure=empty_path_figure,
                                                config={'displayModeBar':False, 'displaylogo':False},
                                            ),
                                        ]),
                                    ]),
                                ])
                                for comp in ['seed', 'generator']
                            ]),
                            dbc.Col(width=6, children=[
                                dbc.Card(style={'height':'100vh'}, children=[
                                    dbc.InputGroup(
                                        size='sm',
                                        children=[
                                            dbc.InputGroupAddon(
                                                addon_type='append',
                                                children=[
                                                    dbc.Button(
                                                        id='fractal-button-clear',
                                                        children='Clear',
                                                        color='primary',
                                                        n_clicks=0,
                                                    ),
                                                ],
                                            ),
                                            dbc.InputGroupAddon(
                                                addon_type='append',
                                                children=[
                                                    dbc.Button(
                                                        id='fractal-button-iterate',
                                                        children='Generate',
                                                        color='warning',
                                                        n_clicks=0,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    dcc.Store(
                                        id='fractal-store-iterations',
                                        data={},
                                    ),
                                    dcc.Graph(
                                        id='fractal-graph-iterations',
                                        style={'height':'100%'},
                                        config={'displayModeBar':False, 'displaylogo':False},
                                        figure=empty_figure,
                                    )
                                ])
                            ])
                        ])
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
    [
        ddp.Output('rubik-store-state', 'data'),
        ddp.Output('rubik-table-history', 'data'),
    ],
    [
        ddp.Input('rubik-button-clear', 'n_clicks'),
        ddp.Input('rubik-button-load', 'n_clicks'),
        ddp.Input('rubik-button-scramble', 'n_clicks'),
        ddp.Input('rubik-graph-state', 'clickData'),
    ],
    [
        ddp.State('rubik-select-dim', 'value'),
        ddp.State('rubik-select-scramble', 'value'),
        ddp.State('rubik-store-state', 'data'),
        ddp.State('rubik-table-history', 'data'),
    ],
)
def set_cube_state(*args:list) -> tp.List[dict]:
    trigger = dash.callback_context.triggered[0]
    if not trigger['value'] or trigger['prop_id'].endswith('clear.n_clicks'):
        return [], []

    *_, dim, scramble, state, history = args
    cube = RubiksCube(dim=int(dim), state=state)
    if trigger['prop_id'].endswith('load.n_clicks'):
        cube = RubiksCube(dim=int(dim), state=None)
        return cube.get_state(), []

    if trigger['prop_id'].endswith('scramble.n_clicks'):
        operation = cube.scramble(n=int(scramble))
        history.extend({'move':move} for move in operation.split(','))
        return cube.get_state(), history

    if trigger['prop_id'].endswith('state.clickData'):
        faces, axes = zip(*RubiksCube._face_axes.items())
        point = trigger['value']['points'][0]
        coord = {axis:point[axis] for axis in ['x', 'y', 'z']}
        axis = max(coord.keys(), key=lambda axis:abs(coord[axis]))
        axis += '+' if coord[axis]>0 else '-'
        face = list(faces)[list(axes).index(axis)]
        cube.rotate(operation=face)
        history.append({'move':face})
        return cube.get_state(), history

    return cube.get_state(), history
    
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
        return base_figure, None
    figure = RubiksCube(dim=int(dim), state=state).get_figure()
    for trace in figure['data']:
        trace.update({
            'hoverinfo':'none' if trace['type']=='mesh3d' else 'skip',
            'hovertemplate':'',
            'name':None,
        })
    figure['layout'].update({
        **base_figure['layout'],
        'annotations':base_figure['layout']['annotations'][1:],
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
    return not trigger['value'].get('data', [])

####################################################################################################
# PIVOT TABLE

@app.callback(
    [
        ddp.Output('pivot-tabulator-raw', 'data'),
        ddp.Output('pivot-tabulator-raw', 'columns'),
    ],
    [
        ddp.Input(f'pivot-dmi-{library}-{source}-{func}', 'n_clicks')
        for library, sources in datasets.items()
        for source, funcs in sources.items()
        for func in funcs
    ],
)
def load_raw_data(*n_clicks:tp.List[str]) -> tp.List[dict]:
    trigger = dash.callback_context.triggered[0]
    if not trigger['value']:
        raise dxc.PreventUpdate
    
    comp = trigger['prop_id'].rsplit('.', maxsplit=1)[0]
    *_, library, source, func = comp.split('-')

    if library=='plotly':
        data = getattr(ptd, func)()
    elif library=='sklearn':
        output = getattr(skd, func)()
        if isinstance(output, sku.Bunch):
            
            Xdat = output.data
            if len(Xdat.shape)==1:
                Xdat = Xdat[:, np.newaxis]

            Xcol = output.get('feature_names', range(Xdat.shape[1]))

            X = dict(zip(Xcol, Xdat.T))
        data = pd.DataFrame(X)
    else:
        data = pd.DataFrame()

    records = data.to_dict(orient='records')
    columns = [
        {
            'title':col,
            'field':col,
            'hozAlign':'center',
        }
        for col in data.columns
    ]
    return records, columns

@app.callback(
    ddp.Output('pivot-div-agg', 'children'),
    [ddp.Input('pivot-tabulator-raw', 'data')],
)
def load_agg_data(records:tp.List[dict]) -> dpv.PivotTable:
    n = sum(len(col) for col in records[0])
    return dpv.PivotTable(id=str(pd.Timestamp.now()), data=records, unusedOrientationCutoff=n+1)

####################################################################################################
# FRACTAL

for comp in ['seed', 'generator']:

    @app.callback(
        ddp.Output(f'fractal-graph-{comp}', 'figure'),
        [ddp.Input(f'fractal-canvas-{comp}', 'json_data')],
    )
    def parse_canvas(data:str) -> dict:
        data = json.loads(data)
        figure = {**empty_path_figure, 'data':[]}
        if not data['objects']:
            return figure

        lines = pd.DataFrame(data['objects'])
        moves = lines[['x2', 'y2']].sub(lines[['x1', 'y1']].values)
        moves.rename(columns=lambda s:s[0], inplace=True)
        path = pd.concat([pd.DataFrame([{'x':0, 'y':0}]), moves.cumsum()])
        path['y'] *= -1

        figure['data'] = [{'type':'scatter', 'x':path['x'], 'y':path['y'], 'showlegend':False}]
        figure['layout']['annotations'] = []
        return figure

@app.callback(
    ddp.Output(f'fractal-store-iterations', 'data'),
    [
        ddp.Input(f'fractal-button-clear', 'n_clicks'),
        ddp.Input(f'fractal-button-iterate', 'n_clicks'),
        ddp.Input(f'fractal-graph-seed', 'figure'),
        ddp.Input(f'fractal-graph-generator', 'figure'),
    ],
    [ddp.State(f'fractal-store-iterations', 'data')],
)
def store_iterations(clear:int, iterate:int, seed:dict, generator:dict, iterations:dict) -> dict:
    trigger = dash.callback_context.triggered[0]
    if not trigger['prop_id'].endswith('iterate.n_clicks'):
        return {}

    seed = list(zip(seed['data'][0]['x'], seed['data'][0]['y']))
    generator = list(zip(generator['data'][0]['x'], generator['data'][0]['y']))
    fractal = Fractal(seed=seed, generator=generator)
    fractal._iterations = {int(n):pd.DataFrame(iteration) for n, iteration in iterations.items()}
    fractal._iterations = {} # TODO: fix pre-cached iterations bug

    n = 1+max(map(int, iterations.keys()), default=-1)
    if n>5:
        return {} # TODO: Create front-end for 'fractal budget' to not overload process.
    
    iterations[n] = fractal.get_iteration(n=n).to_dict(orient='records')    
    return iterations

@app.callback(
    ddp.Output(f'fractal-graph-iterations', 'figure'),
    [ddp.Input(f'fractal-store-iterations', 'data')],
)
def graph_iterations(iterations:dict) -> dict:
    figure = {**empty_figure, 'data':[]}
    if not iterations:
        return figure

    for i, n in enumerate(sorted(iterations.keys(), reverse=True)):
        iteration = pd.DataFrame(iterations[n])
        figure['data'].append({
            'type':'scatter',
            'x':iteration.iloc[:, 0],
            'y':iteration.iloc[:, 1],
            'name':f'Iteration {n}',
            'visible':True if i==0 else 'legendonly',
        })

    return figure

####################################################################################################
# DEPLOY

if __name__ == '__main__':
    kwargs = su.get_cli_kwargs()
    app.run_server(**kwargs)