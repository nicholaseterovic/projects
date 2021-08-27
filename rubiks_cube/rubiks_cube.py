# Nicholas Eterovic 2020Q3
####################################################################################################

# Open-source packages.
import numpy as np
import pandas as pd
import typing as tp
import itertools as it

# Dash imports.
import dash
import dash_tabulator as dtb
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

# In-house packages.
import constants.constants as constants

####################################################################################################

class RubiksCube:
    
    # Class attributes.
    _axes = ['x', 'y', 'z']
    _colors = ['yellow', 'green', 'red', 'white', 'blue', 'orange']
    _face_axes = {'L':'x-', 'R':'x+', 'U':'y+', 'D':'y-', 'F':'z+', 'B':'z-'}

    def __init__(self:object, dim:int=3, state:tp.List[dict]=None) -> object:
        '''
        ____________________________________________________________
        > Instantiate a Rubik's cube.

        Args:
            dim: Positive integer dimension of the cube.
            state: Initial state of the cube, defaults to solved state if None.

        Returns:
            RubiksCube object.
        ____________________________________________________________
        '''
        self.dim = dim
        self.state = state
        
        if state is not None:
            self._state = state
        else:
            self._state = []
            for c, color in enumerate(self._colors):
                z = self._axes[c%3]
                x, y = [axis for axis in self._axes if axis!=z]
                self._state.extend([
                    {'color':color, z:(-1 if c%2 else +1)*dim, x:i, y:j}
                    for i, j in it.product(range(1-dim, dim), repeat=2)
                    if i%2!=dim%2 and j%2!=dim%2
                ])

        self._state = pd.DataFrame(self._state)
        self._history = []

    @property
    def is_solved(self:object) -> bool:
        return self._state.groupby('color')[self._axes].nunique().eq(1).sum(axis=1).eq(1).all()

    ###############################################################################################
    # GETTERS/SETTERS
    
    def get_state(self:object) -> list:
        return self._state.to_dict(orient='records')
    
    def set_state(self:object, state:tp.List[dict]) -> object:
        self._state = pd.DataFrame(state)
        return self
    
    ###############################################################################################
    # ATOMIC OPERATIONS
        
    def rotate(self:object, rotations:tp.Union[str, tp.List[str]]) -> tp.List[str]:
        '''
        ____________________________________________________________
        > Rotates the cube using (string-of-comma-seperated) rotations.
        
        Output:
            Comma-seperated sequence of applied rotations.
            
        A rotation '<m><F><n>' has three components:
        
        * A face '<F>' to rotate, one of 'F', 'B', 'L', 'R', 'U', 'D'.
        * A +ve integer '<n>' of clockwise rotations, omit to perfom a single rotation.
        * A +ve integer '<m>' of layers to rotate, omit to rotate a single layer.
        
        Examples:
        rotation='F' rotates the front-face by 90-degrees clockwise.
        rotation='R2' rotates the right-face by 180-degrees clockwise.
        rotation='2T3' rotates the top-face top-two-layers by 90-degrees anti-clockwise.
        ____________________________________________________________
        '''
        if isinstance(rotations, str):
            rotations = list(filter(None, rotations.upper().strip(' ').split(',')))
        if not rotations:
            return []
        
        # Unpack first operation.
        rotation, *remaining = rotations
        i = min(i for i, char in enumerate(rotation) if char.isupper())
        prfx, face, sffx = rotation[:i], rotation[i], rotation[i+1:]
        
        # Parse valid face, number of layers, and number of radions.
        if face not in self._face_axes:
            raise ValueError(f'Invalid operation face "{face}" in "{rotation}"')
        if not prfx:
            layers = 1
            rotation = f'1{rotation}'
        elif all(char.isdigit() for char in prfx):
            layers = [int(digit) for digit in prfx]
        else:
            raise ValueError(f'Invalid operation prefix "{prfx}" in "{rotation}"')
        if not sffx:
            rads = np.pi/2
            rotation = f'{rotation}1'
        elif sffx.isnumeric():
            rads = int(sffx)*np.pi/2
        else:
            raise ValueError(f'Invalid rotation suffix "{sffx}" in "{rotation}"')
        
        # Apply rotation to affected stickers.
        matrix = self._get_rotation_matrix(face=face, rads=rads)
        stickers = self._get_stickers(face=face, layers=layers)
        index = stickers.index
        self._state.loc[index, self._axes] = self._state.loc[index, self._axes].dot(matrix)
        
        # Append rotation to history; recurse on remaining rotations.
        self._history.append(rotation)
        return [rotation, *self.rotate(rotations=remaining)]
    
    def _get_stickers(self:object, face:str, layers:tp.Union[int, tp.List[int]]=1) -> pd.DataFrame:
        if not isinstance(layers, list):
            layers = [layers]
        levels = [1+self.dim-2*layer+margin for layer in layers for margin in (+1, 0, -1)]
        axis, sign = self._face_axes[face]
        mask = self._state[axis].mul(-1 if sign=='-' else +1).isin(levels)
        index = mask.loc[mask].index
        stickers = self._state.loc[index]
        return stickers
        
    def _get_rotation_matrix(self:object, face:str, rads:float=np.pi/2) -> pd.DataFrame:
        # Unpack rotation axis and angle.
        axis, sign = self._face_axes[face]
        rads *= -1 if sign=='-' else +1
        # Construct 3D rotation matrix.
        cos, sin = np.cos(rads), (-1 if axis=='y' else +1)*np.sin(rads)
        rotation = pd.DataFrame(data=0, index=self._axes, columns=self._axes)
        rotation.loc[axis, axis] = 1
        to_rotate = rotation.index.difference([axis])
        rotation.loc[to_rotate, to_rotate] = [
            [+cos, -sin],
            [+sin, +cos],
        ]
        return rotation.round(0)

    ###############################################################################################
    # COMPOSITIE OPERATIONS
    
    def scramble(self:object, n:int=100, turns:bool=True, layers:bool=True) -> tp.List[str]:
        '''
        ____________________________________________________________
        > Performs <n> random moves on the cube.
        
        Output:
            List of applied rotations.
        ____________________________________________________________
        '''
        rotations = list(np.random.choice(a=list(self._face_axes), size=n))
        if turns:
            array = np.random.randint(low=1, high=4, size=n)
            rotations = [face+str(turn) for face, turn in zip(rotations, array)]
        if layers:
            array = np.random.randint(low=1, high=self.dim+1, size=n)
            rotations = [str(layer)+face for layer, face in zip(array, rotations)]

        return self.rotate(rotations=rotations)
        
    def unscramble(self:object) -> tp.List[str]:
        '''
        ____________________________________________________________
        > 'Solves' the cube by undoing rotations back to the initial state.
        
        Output:
            List of applied rotations.
        ____________________________________________________________
        '''
        rotations = [f'{move[:-1]}{-int(move[-1])%4}' for move in reversed(self._history)]
        return self.rotate(rotations=rotations)

    ###############################################################################################
    # SOLVE OPERATIONS

    def solve(self:object) -> tp.List[str]:
        if self.is_solved:
            return []
        return [
            *self._solve_daisy(),
        ]

    def _solve_daisy(self:object) -> tp.List[str]:
        return [
            *self._rotate_cube(identifier_from='yellow', identifier_to='U'),
            *self._solve_daisy_middle_layer(),
        ]
    
    def _solve_daisy_middle_layer(self:object) -> tp.List[str]:
        return []
    
    ###############################################################################################
    # UTILITIES

    def _get_center_sticker(self:object, identifier:str='F') -> pd.Series:
        if identifier in self._colors:
            points = self._state.loc[lambda df:df['color'].eq(identifier)]
        elif identifier in self._face_axes.keys():
            axis, sign = self._face_axes[identifier]
            coord = self.dim*(-1 if '-' in sign else +1)
            points = self._state.loc[lambda df:df[axis].eq(coord)]
        else:
            raise TypeError(identifier)
        sticker_index = points[self._axes].eq(0).sum(axis=1).eq(2).idxmax()
        sticker = self._state.loc[sticker_index]
        return sticker

    def _get_face(self:object, sticker:pd.Series) -> str:
        axis = sticker[self._axes].astype(float).abs().idxmax()
        code = axis + ('+' if sticker[axis]==self.dim else '-')
        face = max(self._face_axes.keys(), key=lambda key:self._face_axes[key]==code)
        return face

    def _rotate_cube(self:object, identifier_from:str, identifier_to:str) -> tp.List[str]:
        sticker_from = self._get_center_sticker(identifier=identifier_from)
        sticker_to = self._get_center_sticker(identifier=identifier_to)
        sticker_diff = sticker_to[self._axes] - sticker_from[self._axes]
        if sticker_diff.eq(0).all():
            return []

        axis = sticker_diff.eq(0).idxmax()
        face = max(self._face_axes.keys(), key=lambda key:self._face_axes[key].startswith(axis))
        layers = ''.join(map(str, range(1, self.dim+1)))

        if sticker_diff.abs().eq(2*self.dim).any():
            return self.rotate(rotations=f'{layers}{face}2')        
        return [
            *self.rotate(rotations=f'{layers}{face}'),
            *self._rotate_cube(
                identifier_from=sticker_from['color'],
                identifier_to=self._get_face(sticker_to),
            ),
        ]

    ###############################################################################################
    # VISUALIZATION
    
    def get_labels(self:object) -> pd.DataFrame:
        return pd.DataFrame([
            {
                'text':face,
                **{
                    axis:(self.dim+1)*(-1 if '-' in desc else +1)*int(axis in desc)
                    for axis in self._axes
                },
            }
            for face, desc in self._face_axes.items()
        ])
        
    def get_mesh(self:object) -> pd.DataFrame:
        return pd.DataFrame([
            {
                'color':sticker['color'],
                'ix':sticker['x'], 'iy':sticker['y'], 'iz':sticker['z'],
                f'j{x}':sticker[x]+d, f'j{y}':sticker[y]+1 , f'j{z}':sticker[z],
                f'k{x}':sticker[x]+d, f'k{y}':sticker[y]-1 , f'k{z}':sticker[z],
            }
            for z in self._axes
            for _, sticker in self._state.loc[self._state[z].abs().eq(self.dim)].iterrows()
            for x, y in it.permutations([a for a in self._axes if a!=z])
            for d in [-1, +1]
        ])
    
    def get_figure(self:object) -> dict:
        '''
        ____________________________________________________________
        > Returns a 3D figure dictionary.
        
        Output:
            Plotly figure dictionary.
        ____________________________________________________________
        '''
        # Initialize figure with empty data.
        figure = {
            'data':[],
            'layout':{
                'uirevision':0,
                'scene':{
                    'camera':{'up':{'x':0, 'y':1, 'z':0}, 'eye':{'x':-1, 'y':1, 'z':-1}},
                    **{
                        f'{axis}axis':{'autorange':'reversed' if axis!='y' else True, 'visible':False}
                        for axis in self._axes
                    },
                },
            },
        }
        
        # Append wire-edge traces.
        steps = [step for step in range(-self.dim, self.dim+1) if step%2==self.dim%2]
        x = [*steps, *[self.dim for s in steps], *reversed(steps), *[-self.dim for s in steps]]
        y = [*[self.dim for s in steps], *steps, *[-self.dim for s in steps], *reversed(steps)]
        for i, axis in enumerate(self._axes):
            var = [a for a in self._axes if a!=axis]
            figure['data'].extend([
                {
                    'type':'scatter3d', axis:[step for _ in zip(x, y)], var[0]:x, var[1]:y, 
                    'mode':'lines', 'line':{'color':'black', 'width':20}, 'name':'Frame',
                    'legendgroup':'frame', 'showlegend':i==j==0,
                }
                for j, step in enumerate(steps)
            ])
        
        # Append mesh-face trace.
        mesh = self.get_mesh()
        xyz = list(set(
            (x, y, z)
            for v in ['i', 'j', 'k']
            for x, y, z in mesh[[f'{v}x', f'{v}y', f'{v}z']].values
        ))
        x, y, z = zip(*xyz)
        figure['data'].append({
            'type':'mesh3d', 'x':x, 'y':y, 'z':z, 'facecolor':mesh['color'],
            **{
                v:mesh[[f'{v}x', f'{v}y', f'{v}z']].apply(lambda row:xyz.index(tuple(row)), axis=1)
                for v in ['i', 'j', 'k']
            },
        })
        
        # Append text-labels trace.
        labels = self.get_labels()
        figure['data'].append({
            'type':'scatter3d', 'x':labels['x'], 'y':labels['y'], 'z':labels['z'], 'text':labels['text'],
            'mode':'text', 'textposition':'middle center', 'name':'Faces', 'textfont':{'size':30},
        })
        
        return figure

####################################################################################################
# LAYOUT

empty_cube_figure = {
    'layout':{
        'dragmode':'orbit',
        'uirevision':'keep',
        'margin':{'t':0,'b':0,'l':0,'r':0, 'pad':0},
        'xaxis':{'visible':False},
        'yaxis':{'visible':False},
        'showlegend':False,
        'annotations':[
            # Center annotation.
            {
                'text':'<b>Select a Cube Size and Load</b>',
                'xref':'paper',
                'yref':'paper',
                'x':0.5,
                'y':0.5,
                'showarrow':False,
                'font':{'size':30},
            },
            # Corner annotations.
            *[
                {'text':text, 'xref':'paper', 'yref':'paper', 'x':x, 'y':y, 'showarrow':False}
                for x, y, text in [
                    (0.1, 0.9, '<b>Mouse-wheel</b><br>to zoom in and out'),
                    (0.9, 0.9, '<b>Left-click and drag</b><br>(outside the cube)<br>to rotate the cube'),
                    (0.1, 0.1, '<b>Left-click on a cube face</b><br>to rotate by 90º clockwise'),
                    (0.9, 0.1, '<b>Right-click and drag</b><br>(outside the cube)<br>to reposition the cube'),
                ]
            ],
        ],
    },
}


app_layout = [
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown('''
                # Solving the Rubik's Cube
                ***

                ### Introduction
                ***

                  This project originated in the Summer of 2020
                with a sudden motivation to learn how to solve a **Rubik's cube**.
                Little did I know of how deep the cubing rabbit's hole goes!

                  As I sat fiddling and memorizing the various algorithms needed to assemble colors,
                I decided that a better way to learn the cube's intricacies was instead to *code it up*.

                  The result is a *virtual cube* that I am proud to share with you.
                If you are curious,
                I have documented below my modelling and implementation approach.
            '''),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.InputGroupAddon(addon_type='append', children=[
                        dbc.Button(
                            id='rubik-button-clear',
                            children='Clear',
                            n_clicks=0,
                            color='warning',
                            disabled=False,
                        ),
                    ]),
                    dbc.InputGroupAddon(addon_type='prepend', children=[
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
                        options=[
                            {'label':f'{n}x{n} Cube', 'value':n}
                            for n in range(1, 6)
                        ],
                    ),
                    dbc.InputGroupAddon(addon_type='prepend', children='On face click:'),
                    dbc.Select(
                        id='rubik-select-layer',
                        value=1,
                        options=[
                            {'label':f'Rotate layer {layer}', 'value':layer}
                            for layer in range(1, 4)
                        ],
                    ),
                    dbc.InputGroupAddon(addon_type='prepend', children=[
                        dbc.Button(
                            id='rubik-button-scramble',
                            children='Scramble',
                            n_clicks=0,
                            color='primary',
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
                    dbc.InputGroupAddon(addon_type='append', children=[
                        dbc.Button(
                            id='rubik-button-solve',
                            children='Solve',
                            n_clicks=0,
                            color='primary',
                            disabled=False,
                        ),
                    ]),
                ],
            ),
        ]),
        dcc.Store(id='rubik-store-state', data=[]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(width=10, children=[
                    dcc.Graph(
                        id='rubik-graph-state',
                        style={'height':'100vh', 'border':'1px black solid'},
                        config={'scrollZoom':True, 'displayModeBar':False, 'displaylogo':False},
                        figure=empty_cube_figure,
                    ),
                ]),
                dbc.Col(width=2, children=[
                    dtb.DashTabulator(
                        id='rubik-table-history',
                        data=[],
                        columns=[
                            {
                                'title':'Move Sequence (Click to Revert)',
                                'columns':[
                                    {'title':'Index', 'field':'i', 'hozAlign':'center', 'headerSort':False},
                                    {'title':'Move', 'field':'move', 'hozAlign':'center', 'headerSort':False},
                                ]
                            },
                        ],
                        options={
                            'placeholder':'None',
                            'layout':'fitDataStretch',
                            'height':'100vw',
                            'minHeight':'100vh',
                            'maxHeight':'100vh',
                            'selectable':'false',
                        },
                    ),
                ]),
            ]),
        ]),
    ]),
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown('''
                ### The Group of Rotations
                ***

                  An unsurprising fact is that there are finitely many cube configurations;
                beginning from a solved cube,
                any (possible) state can be represented by its sequence of intermediate rotations.

                  Extending this idea, one can model the cube's rotations with a *group*,
                an algebraic structure $(G, \\times)$ consisting of a set $G$ equipped with an operation $\\times$.

                  Here, the set $G$ consists of all **finite sequences**
                of the **U**p, **D**own, **L**eft, **R**ight, **T**op, and **B**ottom **quarter-turn rotations**:

                $$ G = \\lbrace U, D, L, R, T, B, \dots \\rbrace $$

                  The group operation $\\times$ maps any two elements of $G$ to their *composition*,
                which by definition is also in $G$:

                $$ \\times : G^{2} \\rightarrow G $$

                Now, $(G,\\times)$ qualifies as a group as it satisfies the defining assumptions:

                * **Associativity of the operation:**

                  $$ \\forall f, g, h \in G, \\ (f \\times g) \\times h = f \\times (g \\times h) $$

                  In other words, it does not matter how you group a sequence of rotations -
                only that they are executed in the same order.

                * **Existence of an identity:**
                
                  $$ \exists \\ i \in G : \\forall g \in G, \\ g \\times i = i = i \\times g $$

                  For the Rubik's cube group, the identity is the empty sequence of rotations i.e doing nothing.

                * **Existence of inverses:**
                
                  $$ \\forall g \in G, \exists \\ g^{-1} : g \\times g^{-1} = i $$

                  A single-face rotation $ g \in \\lbrace U, D, L, R, T, B \\rbrace $ has a natural inverse:
                that same rotation performed thrice more.

                  That is,
                $g^{-1} = g^{3} \in G: g \\times g^{-1} = g \\times g^{3} = g \\times (g \\times g \\times g) = i $.

                  A sequence of rotations has a more involved inverse: the reverse-sequence of inverse-rotations.

                  For example,
                $ (L \\times U \\times B \\times R)^{-1} =
                R^{-1} \\times B^{-1} \\times U^{-1} \\times L^{-1} = 
                R^{3} \\times B^{3} \\times U^{3} \\times L^{3} $.

                Identifying the Rubik's cube group allows the application of *group theory* and its numerous results.

                I invite the reader to [learn more!](https://en.wikipedia.org/wiki/Rubik%27s_Cube_group)

            '''),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        ddp.Output('rubik-button-reset', 'n_clicks'),
        [ddp.Input('tabs-projects', 'value')],
        [ddp.State('rubik-button-reset', 'n_clicks')],
    )
    def click_reset(tab:str, n_clicks:int) -> int:
        if tab != 'rubik' or n_clicks > 0:
            raise dex.PreventUpdate
        return n_clicks + 1

    @app.callback(
        [
            ddp.Output('rubik-select-layer', 'options'),
            ddp.Output('rubik-select-layer', 'value'),
            ddp.Output('rubik-store-state', 'data'),
            ddp.Output('rubik-table-history', 'data'),
        ],
        [
            ddp.Input('rubik-button-clear', 'n_clicks'),
            ddp.Input('rubik-button-reset', 'n_clicks'),
            ddp.Input('rubik-button-scramble', 'n_clicks'),
            ddp.Input('rubik-button-solve', 'n_clicks'),
            ddp.Input('rubik-graph-state', 'clickData'),
            ddp.Input('rubik-table-history', 'rowClicked'),
            ddp.Input('rubik-select-dim', 'value'),
        ],
        [
            ddp.State('rubik-select-layer', 'value'),
            ddp.State('rubik-select-scramble', 'value'),
            ddp.State('rubik-store-state', 'data'),
            ddp.State('rubik-table-history', 'data'),
        ],
    )
    def set_cube_state(*args:list) -> tp.Tuple[object, ...]:
        trigger = dash.callback_context.triggered[0]
        if not trigger['value'] or trigger['prop_id'].endswith('clear.n_clicks'):
            # Clear cube.
            return constants.EMPTY_OPTIONS, '', [], [], 

        # Unpack arguments and enforce data types.
        *_, dim, layer, scramble, state, history = args
        dim = int(dim)
        layer = int(layer) if layer else 1
        scramble = int(scramble)
        
        options = [
            {'label':f'Rotate layer {layer}', 'value':layer}
            for layer in range(1, 1+dim)
        ]
        layer = min(layer, dim)

        if trigger['prop_id'].endswith('reset.n_clicks') or trigger['prop_id'].endswith('dim.value'):
            # Load new cube.
            cube = RubiksCube(dim=dim, state=None)
            return options, layer, cube.get_state(), []

        if trigger['prop_id'].endswith('history.rowClicked'):
            # Revert cube.
            i = trigger['value']['i']
            history = [move for move in history if move['i']<i]
            cube = RubiksCube(dim=dim, state=None)
            rotations = [move['move'] for move in history]
            cube.rotate(rotations=rotations)
            return options, layer, cube.get_state(), history

        cube = RubiksCube(dim=dim, state=state)
        
        if trigger['prop_id'].endswith('scramble.n_clicks'):
            # Scramble cube.
            rotations = cube.scramble(n=scramble)

        if trigger['prop_id'].endswith('solve.n_clicks'):
            # Solve cube.
            rotations = cube.solve()

        if trigger['prop_id'].endswith('state.clickData'):
            # Rotate face of cube.
            faces, axes = zip(*RubiksCube._face_axes.items())
            point = trigger['value']['points'][0]
            coord = {axis:point[axis] for axis in ['x', 'y', 'z']}
            axis = max(coord.keys(), key=lambda axis:abs(coord[axis]))
            axis += '+' if coord[axis]>0 else '-'
            face = list(faces)[list(axes).index(axis)]
            rotations = f'{layer}{face}'
            rotations = cube.rotate(rotations=rotations)

        n = len(history)
        history.extend({'move':rotation, 'i':n+i} for i, rotation in enumerate(rotations))
        return options, layer, cube.get_state(), history
        
    @app.callback(
        ddp.Output('rubik-graph-state', 'figure'),
        [ddp.Input('rubik-store-state', 'data')],
        [ddp.State('rubik-select-dim', 'value')],
    )
    def graph_cube_state(state:list, dim:str) -> dict:
        if not state:
            return empty_cube_figure
        dim = int(dim)
        cube = RubiksCube(dim=dim, state=state)
        figure = cube.get_figure()
        for trace in figure['data']:
            # Disable hover information.
            trace.update({
                'hoverinfo':'none' if trace['type']=='mesh3d' else 'skip',
                'hovertemplate':'',
                'name':None,
            })
        figure['layout'].update({
            **empty_cube_figure['layout'],
            # Remove center annotation.
            'annotations':empty_cube_figure['layout']['annotations'][1:],
        })
        return figure

    @app.callback(
        [
            ddp.Output('rubik-button-scramble', 'disabled'),
            ddp.Output('rubik-button-solve', 'disabled'),
        ],
        [ddp.Input('rubik-store-state', 'data')],
        [ddp.State('rubik-select-dim', 'value')],
    )
    def disable_buttons(state:tp.List[str], dim:str) -> tp.Tuple[bool, bool]:
        if not state or not dim:
            return True, True
        dim = int(dim)
        if dim != 3:
            return False, True
        return False, False