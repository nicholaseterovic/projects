# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import typing as tp
import itertools as it

# Dash imports.
import dash
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

####################################################################################################

class GameOfLife(object):

    # Class attributes.
    _neighborhood:tp.List[tp.Tuple[int, int]] = list(it.product([-1, 0, +1], repeat=2))
    _min_neighbors:int = 2 # Minimum # neighhors required for a live cell to live on.
    _max_neighbors:int = 3 # Maximum # neighhors allowed for a live cell to live on.
    _pop_neighbors:int = 3 # Required # neighhors required for a dead cell to populate.

    def __init__(self, state:tp.List[tp.Tuple[int, int]]=[], maxstep:int=100) -> object:
        '''
        > Initialize an iterator that yields state evolutions from John Conway's game of life. 
        
        Arguments:
            state: List-of-pairs [(x, y), ...], coordinates of initial live cells.
            maxstep: Maximum number of allowed state evolutions.

        Returns:
            Iterable yielding state evolutions.
        '''
        # Check types.
        if not isinstance(maxstep, int) or maxstep<0:
            raise ValueError(f'Max step must be a positive integer: {maxstep}') 
        if not isinstance(state, list):
            raise ValueError(f'State must be list: {state}')
        for xy in state:
            if not isinstance(xy, tuple):
                raise ValueError(f'State elements must be integer 2-tuples {state}')
            if len(xy) != 2:
                raise ValueError(f'State elements must be integer 2-tuples {state}')
            x, y = xy
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError(f'State elements must be integer 2-tuples {state}')
        # Set attributes.
        self.state = state
        self.maxstep = maxstep
        self._step = 0

    def __iter__(self) -> object:
        return self
    
    def __next__(self) -> tp.List[tp.Tuple[int, int]]:
        '''
        > Return the next state evolution.
        
        Arguments:
            None

        Returns:
            List-of-pairs [(x, y), ...] coordinates of next live cells. 
        '''
        if self._step>self.maxstep:
            raise StopIteration        
        state = GameOfLife._get_next_state(state=self.state)
        self.state = state
        self._step += 1
        return state

    @staticmethod
    def _get_next_state(state:tp.List[tp.Tuple[int, int]]) -> tp.List[tp.Tuple[int, int]]:
        # Generate neighborhoods for candidate cells.
        neighborhoods = [
            ((x+dx, y+dy), (x, y))
            for (dx, dy), (x, y) in it.product(GameOfLife._neighborhood, state)
        ]
        neighborhoods = sorted(neighborhoods, key=lambda x:x[0])
        # Encode (coordinates, num_neighbors, is_alive) for every candidate cell.
        cells = [
            (cell, *map(sum, zip(*map(lambda x:(not x, x), map(lambda x:x[-1]==cell, neighbors)))))
            for cell, neighbors in it.groupby(iterable=neighborhoods, key=lambda x:x[0])
        ]
        # Filter candidate cells to those that live in the next evolution.
        state = [
            (x, y)
            for (x, y), num_neighbors, is_alive in cells
            if GameOfLife._cell_lives(num_neighbors=num_neighbors, is_alive=is_alive)
        ]
        return state
    
    @staticmethod
    def _cell_lives(num_neighbors:int=0, is_alive:tp.Union[bool, int]=False) -> bool:
        '''
        > Determines if a cell becomes alive.
        
        Arguments:
            num_neighbors: Number of neighboring live cells.
            is_alive: Indicates if cell is currently alive.

        Returns:
            Indicator if cell becomes alive.
        '''
        if is_alive:
            if num_neighbors<GameOfLife._min_neighbors:
                # Under-population kills live cell.
                return False
            if num_neighbors>GameOfLife._max_neighbors:
                # Over-population kills live cell.
                return False
            # Stable population maintains live cell.
            return True
        if num_neighbors==GameOfLife._pop_neighbors:
            # Procreation populates dead cell.
            return True
        return False

####################################################################################################
# LAYOUT

app_layout = [
    dbc.Row(no_gutters=True, children=[
        dbc.Col(width=6, children=[
            dbc.Card([
                dbc.CardHeader([
                    dbc.InputGroup(
                        size='sm',
                        children=[
                            dbc.InputGroupAddon(
                                addon_type='prepend',
                                children=dbc.Button(
                                    children='Initial State',
                                    n_clicks=0,
                                    color='dark',
                                    disabled=True,
                                ),
                            ),
                            dbc.InputGroupAddon(
                                addon_type='prepend',
                                children='Dimension:',
                            ),
                            dbc.Input(
                                id='input-gol-seed-dim',
                                debounce=False,
                                value=100,
                                type='number',
                                min=1,
                                max=500,
                                step=1,
                            ),
                            dbc.InputGroupAddon(
                                addon_type='append',
                                children=dbc.Button(
                                    id='button-gol-seed-load',
                                    children='Load',
                                    n_clicks=0,
                                    color='primary',
                                    disabled=False,
                                ),
                            ),
                        ],
                    ),
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id='gol-graph-seed',
                        style={'height':'50vw'},
                        config={'scrollZoom':True, 'displayModeBar':True, 'displaylogo':False},
                        figure={
                            'layout':{
                                'uirevision':'keep',
                                'margin':{'t':0,'b':0,'l':0,'r':0, 'pad':0},
                                'xaxis':{'visible':False},
                                'yaxis':{'visible':False},
                                'showlegend':False,
                                'annotations':[
                                    {
                                        'text':'<b>Select a Dimension and Load</b>',
                                        'xref':'paper',
                                        'yref':'paper',
                                        'x':0.5,
                                        'y':0.5,
                                        'showarrow':False,
                                        'font':{'size':30},
                                    },
                                ],
                            },
                            'data':[{
                            }],
                        },
                    ),
                ]),
            ]),
        ]),
        dbc.Col(width=6, children=[
            dbc.Card([
                dbc.CardHeader([
                    dbc.InputGroup(
                        size='sm',
                        children=[
                        ],
                    ),
                ]),
                dbc.CardBody([
                ]),
            ]),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        [
            ddp.Output('button-gol-seed-load', 'children'),
            ddp.Output('button-gol-seed-load', 'color'),
            ddp.Output('button-gol-seed-load', 'disabled'),
        ],
        [ddp.Input('input-gol-seed-dim', 'value')],
    )
    def set_load_state(dim:int) -> tp.Tuple[str, str, bool]:
        if not dim or not isinstance(dim, int):
            return 'Load', 'primary', True
        return 'Load', 'primary', False