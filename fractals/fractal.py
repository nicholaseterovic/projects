# Nicholas Eterovic 2020Q4
####################################################################################################

# Open-source packages.
import json
import numpy as np
import typing as tp
import pandas as pd
import itertools as it

# In-house packages.
from constants import constants

# Dash packages.
import dash
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

####################################################################################################

class Fractal(object):
    
    def __init__(self:object, seed:tp.List[dict], generator:tp.List[dict]) -> object:
        self.seed = seed
        self.generator = generator

        self._seed = pd.DataFrame(self.seed)
        self._generator = pd.DataFrame(self.generator)

    @staticmethod
    def _get_rotation_matrix(rads:float=np.pi/2) -> pd.DataFrame:
        cos, sin = np.cos(rads), np.sin(rads)
        rotation_matrix = pd.DataFrame([[+cos, -sin], [+sin, +cos]])
        return rotation_matrix
    
    @staticmethod
    def _interpolate(start:pd.Series, end:pd.Series, generator:pd.DataFrame) -> pd.DataFrame:
        
        u_vec = generator.iloc[-1] - generator.iloc[0]
        v_vec = end - start

        u_len = u_vec.pow(2).sum()**.5
        v_len = v_vec.pow(2).sum()**.5

        scale = v_len/u_len
        angle = np.arccos((u_vec*v_vec).sum()/(u_len*v_len))
        if u_vec[0]*v_vec[1]-u_vec[1]*v_vec[0] > 0:
            angle *= -1

        rotation = Fractal._get_rotation_matrix(angle)
        interpolation = generator.sub(generator.iloc[0]).mul(scale).dot(rotation).add(start)
        return interpolation
    
    def get_iteration(self:object, n:int=0) -> pd.DataFrame:
        if not isinstance(n, int) or n<0:
            raise ValueError(n)
        elif n==0:
            return self._seed
        elif n in self._iterations:
            return self._iterations[n]
        else:
            prev_iteration = self.get_iteration(n=n-1)
            iteration = pd.concat(ignore_index=True, objs=[
                Fractal._interpolate(
                    start=prev_iteration.iloc[i],
                    end=prev_iteration.iloc[i+1],
                    generator=self._generator,
                ).iloc[int(i>0):]
                for i in range(len(prev_iteration)-1)
            ])
            self._iterations[n] = iteration
            return iteration

####################################################################################################
# LAYOUT

static_segment_datum = {
    'name':'Static Segments',
    'line':{'color':'black', 'dash':'dash', 'width':5},
}
fractal_segment_datum = {
    'name':'Fractal Segments',
    'line':{'color':'red', 'dash':'dash', 'width':5},
}

example_lines = {
    'seed':{
        'Horizontal Line':[
            {'x0':0, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
        ],
        'Vertical Line':[
            {'x0':0, 'x1':0, 'y0':0, 'y1':1, 'fractal':True},
        ],
        'Diagonal Line':[
            {'x0':0, 'x1':1, 'y0':0, 'y1':1, 'fractal':True},
        ],
        'Unit Triangle':[
            {'x0':0, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            {'x0':1, 'x1':0.5, 'y0':0, 'y1':0.5*3**0.5, 'fractal':True},
            {'x0':0.5, 'x1':0, 'y0':0.5*3**0.5, 'y1':0, 'fractal':True},
        ],
        'Unit Square':[
            {'x0':0, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            {'x0':1, 'x1':1, 'y0':0, 'y1':1, 'fractal':True},
            {'x0':1, 'x1':0, 'y0':1, 'y1':1, 'fractal':True},
            {'x0':0, 'x1':0, 'y0':1, 'y1':0, 'fractal':True},
        ],
    },
    'generator':{
        'Minkowski Sausage':[
            {'x0':0, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            {'x0':1, 'x1':1, 'y0':0, 'y1':1, 'fractal':True},
            {'x0':1, 'x1':2, 'y0':1, 'y1':1, 'fractal':True},
            {'x0':2, 'x1':2, 'y0':1, 'y1':0, 'fractal':True},
            {'x0':2, 'x1':2, 'y0':0, 'y1':-1, 'fractal':True},
            {'x0':2, 'x1':3, 'y0':-1, 'y1':-1, 'fractal':True},
            {'x0':3, 'x1':3, 'y0':-1, 'y1':0, 'fractal':True},
            {'x0':3, 'x1':4, 'y0':0, 'y1':0, 'fractal':True},
        ],
        'Koch Curve':[
            {'x0':0, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            {'x0':1, 'x1':1.5, 'y0':0, 'y1':0.5*3**0.5, 'fractal':True},
            {'x0':1.5, 'x1':2, 'y0':0.5*3**0.5, 'y1':0, 'fractal':True},
            {'x0':2, 'x1':3, 'y0':0, 'y1':0, 'fractal':True},
        ],
        'Cesàro Antisnowflake':[
            {'x0':0, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            {'x0':1, 'x1':1.5, 'y0':0, 'y1':-0.5*3**0.5, 'fractal':True},
            {'x0':1.5, 'x1':2, 'y0':-0.5*3**0.5, 'y1':0, 'fractal':True},
            {'x0':2, 'x1':3, 'y0':0, 'y1':0, 'fractal':True},
        ],
        'Bifurcation':[
            {'x0':0, 'x1':0, 'y0':0, 'y1':1, 'fractal':False},
            {'x0':0, 'x1':-1, 'y0':1, 'y1':2, 'fractal':True},
            {'x0':0, 'x1':1, 'y0':1, 'y1':2, 'fractal':True},
        ],
    },
}

empty_path_figure = {
    'data':[
        {
            **datum,
            'line':{**datum.get('line', {}), 'dash':'none'},
            'type':'scatter',
            'x':[None],
            'y':[None],
            'mode':'lines+markers',
            'hoverlabel':{'namelength':-1},
            'marker':{'size':10},
        }
        for datum in (static_segment_datum, fractal_segment_datum)
    ],
    'layout':{
        **constants.empty_figure['layout'],
        'legend':{'xanchor':'left', 'x':0, 'yanchor':'bottom', 'y':0, 'bgcolor':'rgba(0, 0, 0, 0)'},
        'showlegend':True,
        'dragmode':'drawline',
        'xaxis':{'visible':False},
        'yaxis':{'visible':False, 'scaleanchor':'x'},
        'newshape':fractal_segment_datum,
    },
}

app_layout = [
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown('''
                # Self-Similar Fractals
                ***

                ### Introduction
                ***

                Coming soon!
            '''),
        ]),
    ]),
    dbc.Row(no_gutters=True, children=[
        dbc.Col(width=4, children=[
            dbc.Card([
                dbc.CardHeader([
                    dbc.InputGroup(
                        size='sm',
                        children=[
                            dbc.DropdownMenu(
                                id=f'dropdownmenu-fractal-{path}',
                                label=f'Fractal {path.capitalize()}',
                                color='primary',
                                direction='right',
                                addon_type='prepend',
                                children=[
                                    dbc.DropdownMenuItem(
                                        header=True,
                                        children=f'Examples:',
                                    )
                                ] + [
                                    dbc.DropdownMenuItem(
                                        id=f'dropdownmenuitem-fractal-{key}-{path}',
                                        children=key,
                                        n_clicks=0,
                                    )
                                    for key in example_lines[path].keys()
                                ],
                            ),
                            dbc.Input(
                                f'input-fractal-{path}',
                                value='Custom Linear Shape',
                                disabled=False,
                            ),
                            dbc.InputGroupAddon(
                                children='Modifying:',
                            ),
                            dbc.InputGroupAddon(
                                addon_type='prepend',
                                children=[
                                    dbc.Button(
                                        id=f'button-fractal-{path}-mod',
                                        children=fractal_segment_datum['name'],
                                        color='danger',
                                        n_clicks=1,
                                    ),
                                ],
                            ),
                            dbc.InputGroupAddon(
                                addon_type='prepend',
                                children=[
                                    dbc.Button(
                                        id=f'button-fractal-{path}-undo',
                                        children='Undo',
                                        color='primary',
                                        n_clicks=0,
                                    ),
                                ],
                            ),
                            dbc.InputGroupAddon(
                                addon_type='prepend',
                                children=[
                                    dbc.Button(
                                        id=f'button-fractal-{path}-clear',
                                        children='Clear',
                                        color='primary',
                                        n_clicks=0,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id=f'graph-fractal-{path}',
                        config={'displayModeBar':False, 'displaylogo':False},
                        figure=empty_path_figure,
                    ),
                ])
            ])
            for path in ['seed', 'generator']
        ]),
        dcc.Store(
            id='store-fractal',
            data={'seed':[], 'generator':[]},
        ),
        dbc.Col(width=8, children=[
            dbc.Card(style={'height':'100%'}, children=[
                dbc.CardHeader([
                    dbc.InputGroup(
                        size='sm',
                        children=[
                            dbc.InputGroupAddon(
                                addon_type='append',
                                children=[
                                    dbc.Button(
                                        id='button-fractal-iterate',
                                        children='Fractal Iteration',
                                        color='warning',
                                        n_clicks=0,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id='graph-fractal',
                        config={'displayModeBar':False, 'displaylogo':False},
                        style={'height':'100%'},
                        figure=empty_path_figure,
                    ),
                ]),
            ]),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:
    
    for path in ['seed', 'generator']:
        key = list(example_lines[path].keys())[0]

        @app.callback(
            ddp.Output(f'dropdownmenuitem-fractal-{key}-{path}', 'n_clicks'),
            [ddp.Input('tabs-projects', 'value')],
            [ddp.State(f'dropdownmenuitem-fractal-{key}-{path}', 'n_clicks')],
        )
        def click_reset(tab:str, n_clicks:int) -> int:
            if tab != 'fractal' or n_clicks > 0:
                raise dex.PreventUpdate
            return n_clicks + 1

        @app.callback(
            [
                ddp.Output(f'graph-fractal-{path}', 'figure'),
                ddp.Output(f'button-fractal-{path}-mod', 'children'),
                ddp.Output(f'button-fractal-{path}-mod', 'color'),
                ddp.Output(f'input-fractal-{path}', 'value'),
            ],
            [
                ddp.Input(f'button-fractal-{path}-clear', 'n_clicks'),
                ddp.Input(f'button-fractal-{path}-undo', 'n_clicks'),
                ddp.Input(f'button-fractal-{path}-mod', 'n_clicks'),
                ddp.Input(f'graph-fractal-{path}', 'relayoutData'),
            ] + [
                ddp.Input(f'dropdownmenuitem-fractal-{key}-{path}', 'n_clicks')
                for key in example_lines[path].keys()
            ],
            [
                ddp.State(f'graph-fractal-{path}', 'figure'),
                ddp.State(f'button-fractal-{path}-mod', 'children'),
                ddp.State(f'button-fractal-{path}-mod', 'color'),
                ddp.State(f'input-fractal-{path}', 'value'),
            ],
        )
        def set_path(clear:int, undo:int, mod:int, relayoutData:dict, *args:list, path:str=path) -> dict:
            states = list(args)[len(example_lines[path].keys()):]
            i = mod%2
            trigger = dash.callback_context.triggered[0]
            if trigger['prop_id'].endswith(f'{path}.n_clicks'):
                *_, key, path = trigger['prop_id'].rsplit('.', maxsplit=1)[0].split('-')
                lines = example_lines[path][key]
                for axis in ('x', 'y'):
                    for j in (0, 1):
                        del states[0]['data'][j][axis][1:]
                for line in lines:
                    j = int(line['fractal'])
                    states[0]['data'][j]['x'].extend([line['x0'], line['x1'], None])
                    states[0]['data'][j]['y'].extend([line['y0'], line['y1'], None])
                states[3] = key
                return states

            if trigger['prop_id'].endswith('mod.n_clicks'):
                if i:
                    states[0]['layout']['newshape'] = fractal_segment_datum
                    states[1] = fractal_segment_datum['name']
                    states[2] = 'danger'
                else:
                    states[0]['layout']['newshape'] = static_segment_datum
                    states[1] = static_segment_datum['name']
                    states[2] = 'secondary'
                return states

            X = states[0]['data'][i]['x']
            Y = states[0]['data'][i]['y']
            if trigger['prop_id'].endswith('clear.n_clicks'):
                del X[1:]
                del Y[1:]
                return states
            if trigger['prop_id'].endswith('undo.n_clicks'):
                del X[-3:]
                del Y[-3:]
                return states
            
            XY = [xy for datum in states[0]['data'] for xy in zip(datum['x'], datum['y'])]
            XY = list(filter(all, XY))

            r = 0.05
            lines = [shape for shape in relayoutData.get('shapes', []) if shape['type']=='line']
            for line in lines:
                if XY:
                    D0, D1 = zip(*(
                        (
                            ((x-line['x0'])**2 + (y-line['y0'])**2)**0.5,
                            ((x-line['x1'])**2 + (y-line['y1'])**2)**0.5,
                        )
                        for x, y in XY
                    ))
                    _, (line['x0'], line['y0']) = min(
                        filter(lambda dxy:dxy[0]<r, zip(D0, XY)),
                        key=lambda dxy:dxy[0],
                        default=(0, (line['x0'], line['y0'])),
                    )
                    _, (line['x1'], line['y1']) = min(
                        filter(lambda dxy:dxy[0]<r, zip(D1, XY)),
                        key=lambda dxy:dxy[0],
                        default=(0, (line['x1'], line['y1'])),
                    )
                X.extend([line['x0'], line['x1'], None])
                Y.extend([line['y0'], line['y1'], None])
            return states

    @app.callback(
        ddp.Output(f'store-fractal', 'data'),
        [
            ddp.Input(f'graph-fractal-seed', 'figure'),
            ddp.Input(f'graph-fractal-generator', 'figure'),
        ],
        [ddp.State(f'store-fractal', 'data')],
    )
    def set_fractal(seed:dict, generator:dict, data:dict) -> dict:
        trigger = dash.callback_context.triggered[0]
        if trigger['prop_id'].endswith('figure'):
            path = trigger['prop_id'].rsplit('.', maxsplit=1)[0].rsplit('-', maxsplit=1)[-1]
            data[path] = [
                {'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 'fractal':bool(i)}
                for i, d in enumerate(trigger['value']['data'])
                for x0, y0, x1, y1 in zip(d['x'][1::3], d['y'][1::3], d['x'][2::3], d['y'][2::3])
            ]

            print(pd.DataFrame(data[path]))

        return data

    @app.callback(
        ddp.Output(f'graph-fractal', 'figure'),
        [ddp.Input(f'store-fractal', 'data')],
        [ddp.State(f'graph-fractal', 'figure')],
    )
    def plot_fractal(data:dict, figure:dict) -> dict:
        lines = data['seed']
        for axis in ('x', 'y'):
            for j in (0, 1):
                del figure['data'][j][axis][1:]
        for line in lines:
            j = int(line['fractal'])
            figure['data'][j]['x'].extend([line['x0'], line['x1'], None])
            figure['data'][j]['y'].extend([line['y0'], line['y1'], None])
        return figure