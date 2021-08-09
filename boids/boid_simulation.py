# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import numpy as np
import pandas as pd
import typing as tp
import itertools as it

# Dash imports.
import dash
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

####################################################################################################

class BoidSimulation(object):

    @classmethod
    def from_random_state(
        cls,
        num_boids:int=100,
        loc:float=0,
        scale:float=1,
        **kwargs:dict,
    ) -> object:
        dims = 2
        data = np.random.normal(size=(num_boids, dims*2), loc=loc, scale=scale)
        state = pd.DataFrame(data=data, columns=['px', 'py', 'vx', 'vy'])
        return cls(state=state, **kwargs)

    def __init__(
        self,
        state:pd.DataFrame,
        visibility:float=1,
        seperation:float=1,
        cohesion:float=1,
        alignment:float=1,
        time:float=60,
        step:float=1,
    ) -> object:
        '''
        > Initialize an iterator that yields iterations of a Boid simulation. 
        
        Arguments:
            state: Dataframe with columns 'px', 'py, ..., 'vx', 'vy', ... encoding initial Boids.
                   (px, py, ...) encodes the position of a Boid.
                   (vx, vy, ...) encodes the velocity of a Boid.
            visibility: Radius in which a Boid perceives its neighbors.
            seperation: Strength of repulsion to neighboring Boids.
            cohesion: Strength of attraction to flocks of Boids.
            alignment: Strength of orientation to neighboring Boids.
            time: Length of simulation in seconds.
            step: Length of iteration, in seconds.

        Returns:
            Iterable yielding Boid simulation iterations.
        '''
        # Check types.

        # Set public attributes.
        self.state = state
        self.visibility = visibility
        self.seperation = seperation
        self.cohesion = cohesion
        self.alignment = alignment
        self.time = time
        self.step = step

        # Set internal attributes.
        self._dims:tp.List[str] = ['x', 'y']
        self._N:int = self.time//self.step
        self._n:int = 0

    def __iter__(self) -> object:
        return self
    
    def __next__(self) -> pd.DataFrame:
        '''
        > Return the next iteration of the Boid simulation.
        
        Arguments:
            None

        Returns:
            List-of-pairs [(x, y), ...] coordinates of next live cells. 
        '''
        if self._n  >= self._N:
            raise StopIteration
        state = BoidSimulation._get_next_state(
            state=self.state,
            seperation=self.seperation,
            cohesion=self.cohesion,
            alignment=self.alignment,
            visibility=self.visibility,
            dimensions=self._dims,
        )
        self.state = state
        self._n += 1
        return state

    @staticmethod
    def _get_next_state(
        state:pd.DataFrame,
        seperation:float,
        cohesion:float,
        alignment:float,
        visibility:float,
        dimensions:tp.List[str],
    ) -> pd.DataFrame:

        # Self-cross-product Boids for all (center, neighbor) pairs.
        state['i'] = range(len(state))
        state['j'] = 0
        pairs = pd.merge(
            left=state,
            right=state.add_prefix(prefix='n'),
            left_on='j',
            right_on='nj',
            how='outer',
        )

        # Unpack columns.
        cols = [
            (
                f'p{i}', # Positions
                f'v{i}', # Velocitys
                f'np{i}', # Neighbor positions.
                f'nv{i}', # Neighbor velocitys.
                f'nd{i}', # Neighbor distances.
            )
            for i in dimensions
        ]
        p, v, np, nv, nd = map(list, zip(*cols))

        # Nullify pairs for which the center and neighbor are the same.
        pairs.loc[pairs['i']==pairs['ni'], [*np, *nv]] = None

        # For each dimension:
        for pi, npi, ndi in zip(p, np, nd):
            # Compute neighbor-to-center translations.
            pairs[ndi] = pairs[pi] - pairs[npi]
    
        # Compute neighbor-to-center distances.
        ndmag = pairs[nd].pow(2).sum(axis=1).pow(0.5)

        # Subset pairs to visible neighbors.
        pairs = pairs.loc[ndmag.le(visibility)]

        # For each dimension:
        for ndi in nd:
            # Transform neighbor-to-center translations to repulsions.
            pairs[ndi] /= ndmag.pow(2)

        # Compute neighbor velocity magnitudes.
        nvmag = pairs[nv].pow(2).sum(axis=1).pow(0.5)

        # For each dimension:
        for nvi in nv:
            # Transform neighbor velocities to (unit) neighbor directions.
            pairs[nvi] /= nvmag
            pairs[nvi].where(cond=nvmag.gt(0), other=0, inplace=True)

        # Aggregate neighbor information per center Boid.
        agg_last = {col:'last' for col in (*p, *v)}
        agg_mean = {col:'mean' for col in (*np, *nv, *nd)}
        agg = {**agg_last, **agg_mean}
        groups = pairs.groupby(by='i', as_index=False, sort=False)
        state = groups.agg(func=agg).drop(columns='i')

        # For each dimension:
        for pi, npi in zip(p, np):
            # Transform mean-neighbor positions to center-to-mean-neighbor translations.
            state[npi] -= state[pi]
        
        # For each dimension:
        for pi, vi, npi, nvi, ndi in zip(p, v, np, nv, nd):
            # Compute accelerations.
            ai = 0
            ai += seperation * state.pop(ndi).where(cond=pd.notnull, other=0)
            ai += cohesion * state.pop(npi).where(cond=pd.notnull, other=0)
            ai += alignment * state.pop(nvi).where(cond=pd.notnull, other=0)
            # Update velocities and positions.
            state[vi] += ai
            state[pi] += state[vi]

        return state

####################################################################################################
# LAYOUT

empty_boids_figure = {
    'data':[],
    'frames':[],
    'layout':{
        'dragmode':False,
        'hovermode':'closest',
        'xaxis':{'range':[-10, 10], 'autorange':False},
        'yaxis':{'range':[-10, 10], 'autorange':False, 'scaleanchor':'x'},
        'updatemenus':[
            {
                "type": "buttons",
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 1000, "redraw": False},
                                "fromcurrent": True,
                                "transition": {"duration": 1000, "easing": "linear"},
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                    },
                ],
            },
        ],
        'sliders':[
            {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Year:",
                    "visible": True,
                    "xanchor": "right",
                },
                "transition": {"duration": 1000, "easing": "linear"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [],
            },
        ],
    },
}

app_layout = [
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.InputGroupAddon(addon_type='prepend', children=[
                        dbc.Button(
                            id='button-boids-reset',
                            children='Reset',
                            n_clicks=0,
                            color='primary',
                            disabled=False,
                        ),
                    ]),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Seperation:',
                    ),
                    dbc.Input(
                        id='input-boids-seperation',
                        min=0,
                        placeholder='<Non-negative number>',
                        value=1,
                        disabled=False,
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dcc.Graph(
                id='graph-boids-sim',
                config={'displayModeBar':False, 'displaylogo':False},
                figure=empty_boids_figure,
                style={'height':'80vh'},
            ),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        ddp.Output('button-boids-reset', 'n_clicks'),
        [ddp.Input('tabs-projects', 'value')],
        [ddp.State('button-boids-reset', 'n_clicks')],
    )
    def click_reset(tab:str, n_clicks:int) -> int:
        if tab != 'boids' or n_clicks > 0:
            raise dex.PreventUpdate
        return n_clicks + 1

    @app.callback(
        ddp.Output('graph-boids-sim', 'figure'),
        [ddp.Input('button-boids-reset', 'n_clicks')],
        [ddp.State('graph-boids-sim', 'figure')]
    )
    def reset_graph(n_clicks:int, figure:dict) -> dict:

        states = BoidSimulation.from_random_state(
            num_boids=100,
            loc=0,
            scale=1,
            seperation=0,
            cohesion = 1,
            visibility=100,
        )

        figure['frames'] = [
            {
                'name':n,
                'data':[{
                    'x':state['px'],
                    'y':state['py'],
                    'mode':'markers',
                }],
            }
            for n, state in enumerate(states)
        ]

        figure['data'] = figure['frames'][0]['data']
        figure['layout']['sliders'][0]['step'] = [
            {
                "label": frame['name'],
                "method": "animate",
                "args": [
                    [frame['name']],
                    {"frame": {"duration": 1000, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 1000}}
                ],
                }
            for frame in figure['frames']
        ]
        return figure