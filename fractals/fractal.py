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
    
    # Class attributes.
    unit = pd.Series({'dx':1, 'dy':0})
    example_paths = {
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
                {'x0':0, 'x1':0.5, 'y0':0, 'y1':0.5*3**0.5, 'fractal':True},
                {'x0':0.5, 'x1':1, 'y0':0.5*3**0.5, 'y1':0, 'fractal':True},
                {'x0':1, 'x1':0, 'y0':0, 'y1':0, 'fractal':True},
            ],
            'Unit Square':[
                {'x0':0, 'x1':0, 'y0':0, 'y1':1, 'fractal':True},
                {'x0':0, 'x1':1, 'y0':1, 'y1':1, 'fractal':True},
                {'x0':1, 'x1':1, 'y0':1, 'y1':0, 'fractal':True},
                {'x0':1, 'x1':0, 'y0':0, 'y1':0, 'fractal':True},
            ],
        },
        'generator':{
            'Minkowski Sausage':[
                {'x0':0, 'x1':1/4, 'y0':0, 'y1':0, 'fractal':True},
                {'x0':1/4, 'x1':1/4, 'y0':0, 'y1':1/4, 'fractal':True},
                {'x0':1/4, 'x1':1/2, 'y0':1/4, 'y1':1/4, 'fractal':True},
                {'x0':1/2, 'x1':1/2, 'y0':1/4, 'y1':0, 'fractal':True},
                {'x0':1/2, 'x1':1/2, 'y0':0, 'y1':-1/4, 'fractal':True},
                {'x0':1/2, 'x1':3/4, 'y0':-1/4, 'y1':-1/4, 'fractal':True},
                {'x0':3/4, 'x1':3/4, 'y0':-1/4, 'y1':0, 'fractal':True},
                {'x0':3/4, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            ],
            'Koch Curve':[
                {'x0':0, 'x1':1/3, 'y0':0, 'y1':0, 'fractal':True},
                {'x0':1/3, 'x1':1/2, 'y0':0, 'y1':(1/6)*3**(1/2), 'fractal':True},
                {'x0':1/2, 'x1':2/3, 'y0':(1/6)*3**(1/2), 'y1':0, 'fractal':True},
                {'x0':2/3, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            ],
            'Cesàro Antisnowflake':[
                {'x0':0, 'x1':1/3, 'y0':0, 'y1':0, 'fractal':True},
                {'x0':1/3, 'x1':1/2, 'y0':0, 'y1':(-1/6)*3**(1/2), 'fractal':True},
                {'x0':1/2, 'x1':2/3, 'y0':(-1/6)*3**(1/2), 'y1':0, 'fractal':True},
                {'x0':2/3, 'x1':1, 'y0':0, 'y1':0, 'fractal':True},
            ],
            'Bifurcation':[
                {'x0':0, 'x1':1/2, 'y0':0, 'y1':0, 'fractal':False},
                {'x0':1/2, 'x1':1, 'y0':0, 'y1':1/2, 'fractal':True},
                {'x0':1/2, 'x1':1, 'y0':0, 'y1':-1/2, 'fractal':True},
            ],
            'Lightning Bolt':[
                {'x0':0, 'x1':1/2, 'y0':0, 'y1':1/4, 'fractal':True},
                {'x0':1/2, 'x1':1/2, 'y0':1/4, 'y1':-1/4, 'fractal':True},
                {'x0':1/2, 'x1':1, 'y0':-1/4, 'y1':0, 'fractal':True},
            ],
        },
    }

    def __init__(self:object, seed:tp.List[dict], generator:tp.List[dict]) -> object:
        # Set public attributes.
        self.seed = seed
        self.generator = generator
        # Set internal attributes.
        self._seed = pd.DataFrame(self.seed)
        self._generator = pd.DataFrame(self.generator)
        self._N:int = 1000
        self._n:int = 0

    def __iter__(self) -> object:
        return self
    
    def __next__(self) -> pd.DataFrame:
        if self._n  >= self._N:
            raise StopIteration
        interpolated_seed = Fractal.interpolate_seed(
            seed=self._seed,
            generator=self._generator,
        )
        self._seed = interpolated_seed
        self._n += 1
        return interpolated_seed
    
    @staticmethod
    def interpolate_seed(seed:pd.DataFrame, generator:pd.DataFrame) -> pd.DataFrame:
        if seed.empty or generator.empty:
            return seed
        u = Fractal.unit
        S = seed.copy()
        
        # Enrich seed line(s) properties.
        S['dx'] = S['x1'] - S['x0']
        S['dy'] = S['y1'] - S['y0']
        S['length'] = S[['dx', 'dy']].pow(2).sum(axis=1).pow(0.5)
        S['cross'] = np.where(np.cross(S[['dx', 'dy']], u)>0, -1, 1)
        S['angle'] = S[['dx', 'dy']].dot(u).div(S['length']).map(np.arccos).mul(S['cross'])

        # Interpolate each seed line.
        lines = []
        for i, s in S.iterrows():
            if not s['fractal']:
                # Do not interpolate non-fractal seed line.
                line = s[seed.columns].to_frame().T
            else:
                # Rotate, rescale, and translate generator to interpolate seed line.
                G = generator.copy()
                R = Fractal._get_rotation_matrix(rads=s['angle'])
                G[['x0', 'y0']] = G[['x0', 'y0']].dot(R.T).values * s['length'] + s[['x0', 'y0']].values
                G[['x1', 'y1']] = G[['x1', 'y1']].dot(R.T).values * s['length'] + s[['x0', 'y0']].values                    
                line = G[seed.columns]
            lines.append(line)

        interpolated_seed = pd.concat(lines)
        return interpolated_seed

    @staticmethod
    def _get_rotation_matrix(rads:float=np.pi/2) -> np.ndarray:
        cos, sin = np.cos(rads), np.sin(rads)
        rotation_matrix = np.array([[+cos, -sin], [+sin, +cos]])
        return rotation_matrix

    @staticmethod
    def _get_path_from_figure(figure:dict) -> tp.List[dict]:
        return [
            {'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 'fractal':bool(i)}
            for i, d in enumerate(figure['data'][:2])
            for x0, y0, x1, y1 in zip(d['x'][1::3], d['y'][1::3], d['x'][2::3], d['y'][2::3])
        ]

####################################################################################################
# LAYOUT

# Fractal construction lines.
static_segment_datum = {
    'type':'scatter',
    'name':'Static Segments',
    'hoverlabel':{'namelength':-1},
    'line':{'color':'#7f7f7f', 'dash':'dot', 'width':5},
    'opacity':0.75,
    'x':[None],
    'y':[None],
}
fractal_segment_datum = {
    'type':'scatter',
    'name':'Fractal Segments',
    'hoverlabel':{'namelength':-1},
    'line':{'color':'#1f77b4', 'dash':'dot', 'width':5},
    'opacity':0.75,
    'x':[None],
    'y':[None],
}
interpolate_segment_datum = {
    'type':'scatter',
    'name':'Interpolation Segment',
    'hoverlabel':{'namelength':-1},
    'line':{'color':'#ff7f0e', 'dash':'dot', 'width':5},
    'opacity':0.75,
    'x':[None, 0, 1],
    'y':[None, 0, 0],
}
empty_path_figure = {
    'data':[
        {**datum, 'line':{**datum.get('line', {}), 'dash':'none'}}
        for datum in (static_segment_datum, fractal_segment_datum)
    ],
    'layout':{
        'hovermode':'closest',
        'dragmode':'zoom',
        'newshape':fractal_segment_datum,
        'showlegend':True,
        'xaxis':{'visible':True},
        'yaxis':{'visible':True, 'scaleanchor':'x'},
        'legend':{'orientation':'h', 'bgcolor':'rgba(0, 0, 0, 0)'},
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

                I find fractals a fascinating example of *emergent behaviour* - 
                complicated patterns which are generated by simple rules behind the scenes.

                This project implements a simple method of creating fractals (rather, their finite approximations),
                  using two components:

                * An initial **seed**, which is the fractal's zeroth iteration;
                * An iterative **generator**, which is used to construct the next fractal iteration.

                The algorithm is simple; given a fractal iteration, *interpolate every straight-line segment
                  with a copy of the generator*.
                  This yields the next fractal iteration, for which the algorithm repeats.

                Below is a tool I created to expirement with different combinations of seeds and generators -
                  I was pleasantly surprised with the outcomes!

                One can select from **Fractal Seed** and **Fractal Generator** example libraries or
                  custom-draw lines directly on the construction graphs.

                Once a seed and generator pair is ready, click **Iterate** to get the next fractal iteration.
                  Note that I have capped the number of line segments at 1000 (as it grows exponentially fast).

                Happy Fractalling!
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
                            dbc.InputGroupAddon(
                                addon_type='prepend',
                                children=[
                                    dbc.Button(
                                        id=f'button-fractal-{path}-clear',
                                        children='Clear',
                                        color='warning',
                                        n_clicks=0,
                                    ),
                                ],
                            ),
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
                                    for key in Fractal.example_paths[path].keys()
                                ],
                            ),
                            dbc.Input(
                                f'input-fractal-{path}',
                                value='Custom Linear Shape',
                                disabled=False,
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
                                children='Modifying:',
                            ),
                            dbc.InputGroupAddon(
                                addon_type='prepend',
                                children=[
                                    dbc.Button(
                                        id=f'button-fractal-{path}-mod',
                                        children=fractal_segment_datum['name'],
                                        color='primary',
                                        n_clicks=1,
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
                        figure={
                            'layout':{
                                **empty_path_figure['layout'],
                                'dragmode':'drawline',
                                'title':f'{path.capitalize()} Construction',
                            },
                            'data':[
                                *empty_path_figure['data'],
                                *([interpolate_segment_datum] if path=='generator' else []),
                            ],
                        },
                    ),
                ])
            ])
            for path in ['seed', 'generator']
        ]),
        dcc.Store(
            id='store-fractal',
            data={'seed':[], 'generator':[], 'n':0},
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
                                        children='Iterate',
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
        
        # Load default seed and generator on first tab visit.
        key = list(Fractal.example_paths[path].keys())[0]
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
                for key in Fractal.example_paths[path].keys()
            ],
            [
                ddp.State(f'graph-fractal-{path}', 'figure'),
                ddp.State(f'button-fractal-{path}-mod', 'children'),
                ddp.State(f'button-fractal-{path}-mod', 'color'),
                ddp.State(f'input-fractal-{path}', 'value'),
            ],
        )
        def set_path(clear:int, undo:int, mod:int, relayoutData:dict, *args:list, path:str=path) -> dict:
            states = list(args)[len(Fractal.example_paths[path].keys()):]
            trigger = dash.callback_context.triggered[0]

            # Load example path.
            if trigger['prop_id'].endswith(f'{path}.n_clicks'):
                *_, key, path = trigger['prop_id'].rsplit('.', maxsplit=1)[0].split('-')
                lines = Fractal.example_paths[path][key]
                for axis in ('x', 'y'):
                    for j in (0, 1):
                        del states[0]['data'][j][axis][1:]
                for line in lines:
                    j = int(line['fractal'])
                    states[0]['data'][j]['x'].extend([line['x0'], line['x1'], None])
                    states[0]['data'][j]['y'].extend([line['y0'], line['y1'], None])
                states[3] = key
                return states

            # Change modifying state between fractal and static segments.
            i = mod%2
            if trigger['prop_id'].endswith('mod.n_clicks'):
                if i:
                    states[0]['layout']['newshape'] = fractal_segment_datum
                    states[1] = fractal_segment_datum['name']
                    states[2] = 'primary'
                else:
                    states[0]['layout']['newshape'] = static_segment_datum
                    states[1] = static_segment_datum['name']
                    states[2] = 'secondary'
                return states

            # Indicate custom path.
            states[3] = 'Custom'

            # Clear existing path.
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
            
            # Extract non-null path points.
            XY = [xy for datum in states[0]['data'] for xy in zip(datum['x'], datum['y'])]
            XY = list(filter((None, None).__ne__, XY))

            r = 0.05
            lines = [shape for shape in relayoutData.get('shapes', []) if shape['type']=='line']
            for line in lines:
                if XY:
                    # Snap custom line endpoints to existing points.
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
                # Add custom line to figure data.
                X.extend([line['x0'], line['x1'], None])
                Y.extend([line['y0'], line['y1'], None])
            return states

    @app.callback(
        ddp.Output(f'store-fractal', 'data'),
        [
            ddp.Input(f'graph-fractal-seed', 'figure'),
            ddp.Input(f'graph-fractal-generator', 'figure'),
            ddp.Input('button-fractal-iterate', 'n_clicks'),
        ],
        [ddp.State(f'store-fractal', 'data')],
    )
    def store_fractal(seed:dict, generator:dict, n_clicks:int, data:dict) -> dict:
        trigger = dash.callback_context.triggered[0]
        if trigger['prop_id'].endswith('figure'):
            # Reset seed and generator data on figure edit.
            for path, figure in (('seed', seed), ('generator', generator)):
                data[path] = Fractal._get_path_from_figure(figure=figure)
            data['n'] = 0
            return data
        interpolated_seed = Fractal.interpolate_seed(
            seed=pd.DataFrame(data['seed']),
            generator=pd.DataFrame(data['generator']),
        )
        data['seed'] = interpolated_seed.to_dict(orient='records')
        data['n'] += 1
        return data

    @app.callback(
        [
            ddp.Output('graph-fractal', 'figure'),
            ddp.Output('button-fractal-iterate', 'disabled'),
        ],
        [ddp.Input('store-fractal', 'data')],
        [ddp.State(f'graph-fractal', 'figure')],
    )
    def plot_fractal(data:dict, figure:dict) -> dict:
        n = data['n']
        lines = data['seed']
        for axis in ('x', 'y'):
            for j in (0, 1):
                del figure['data'][j][axis][1:]
        for line in lines:
            j = int(line['fractal'])
            figure['data'][j]['x'].extend([line['x0'], line['x1'], None])
            figure['data'][j]['y'].extend([line['y0'], line['y1'], None])
        figure['layout']['title'] = f'Fractal Iteration #{n}'
        return figure, len(lines)>1000