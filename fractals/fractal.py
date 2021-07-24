# Nicholas Eterovic 2020Q4
####################################################################################################

# Open-source packages.
import json
import numpy as np
import typing as tp
import pandas as pd
import itertools as it
import plotly.offline as py

# In-house packages.
from constants import constants

# Dash packages.
import dash
import dash_canvas as dcv
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

####################################################################################################

class Fractal(object):
    
    def __init__(self:object, seed:tp.List[tuple], generator:tp.List[tuple]) -> object:
        self.seed = seed
        self.generator = generator

        self._seed = pd.DataFrame(dict(enumerate(zip(*self.seed))))
        self._generator = pd.DataFrame(dict(enumerate(zip(*self.generator))))
        self._iterations = {}

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

empty_path_figure = {
    'layout':{
        **constants.empty_figure['layout'],
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

app_layout = [
    dbc.Row(no_gutters=True, children=[
        dbc.Col(width=6, children=[
            dbc.Card(style={'height':'50vh'}, children=[
                dbc.CardHeader([
                    dbc.InputGroup(
                        size='sm',
                        children=[
                            dbc.DropdownMenu(
                                id=f'fractal-ddm-{comp}',
                                label=f'Fractal {comp.capitalize()}',
                                color='link',
                                direction='right',
                                addon_type='prepend',
                                children=[
                                ],
                            ),
                        ],
                    ),
                ]),
                dbc.CardBody([
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
                                ],
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
            ])
            for comp in ['seed', 'generator']
        ]),
        dbc.Col(width=6, children=[
            dbc.Card(style={'height':'100vh'}, children=[
                dbc.CardHeader([
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
                ]),
                dbc.CardBody([
                    dcc.Store(
                        id='fractal-store-iterations',
                        data={},
                    ),
                    dcc.Graph(
                        id='fractal-graph-iterations',
                        style={'height':'100%'},
                        config={'displayModeBar':False, 'displaylogo':False},
                        figure=constants.empty_figure,
                    ),
                ]),
            ]),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

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
        ddp.Output('fractal-graph-iterations', 'figure'),
        [ddp.Input('fractal-store-iterations', 'data')],
    )
    def graph_iterations(iterations:dict) -> dict:
        figure = {**constants.empty_figure, 'data':[]}
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