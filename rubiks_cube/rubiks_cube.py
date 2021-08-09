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
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

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
        ____________________________________________________________
        '''
        self.dim = dim
        self._history = []
        
        if state is None:
            state = []
            for c, color in enumerate(self._colors):
                z = self._axes[c%3]
                x, y = [axis for axis in self._axes if axis!=z]
                state.extend([
                    {'color':color, z:(-1 if c%2 else +1)*dim, x:i, y:j}
                    for i, j in it.product(range(1-dim, dim), repeat=2)
                    if i%2!=dim%2 and j%2!=dim%2
                ])
        self._state = pd.DataFrame(state)

    ###############################################################################################
    # GETTERS/SETTERS
    
    def get_state(self:object) -> list:
        return self._state.to_dict(orient='records')
    
    def set_state(self:object, state:tp.List[dict]) -> object:
        self._state = pd.DataFrame(state)
        return self
    
    ###############################################################################################
    # ATOMIC OPERATIONS
    
    def _get_stickers(self:object, face:str, layers:int=1) -> pd.Series:
        axis, sign = self._face_axes[face]
        return self._state[axis].mul(-1 if sign=='-' else +1).between(self.dim-2*layers, self.dim)
        
    def _get_rotation(self:object, face:str, rads:float=np.pi/2) -> pd.DataFrame:
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
    
    def rotate(self:object, operation:str) -> None:
        '''
        ____________________________________________________________
        > Rotates the cube using (comma-seperated-list-of) operations.
        
        Output:
            None
            
        An operation '<m><F><n>' has three components:
        
        * A face '<F>' to rotate, one of 'F', 'B', 'L', 'R', 'U', 'D'.
        * A +ve integer '<n>' of clockwise rotations, omit to perfom a single rotation.
        * A +ve integer '<m>' of layers to rotate, omit to rotate a single layer.
        
        Examples:
        operation='F' rotates the front-face by 90-degrees clockwise.
        operation='R2' rotates the right-face by 180-degrees clockwise.
        operation='2T3' rotates the top-face top-two-layers by 90-degrees anti-clockwise.
        ____________________________________________________________
        '''
        if not operation:
            return
        
        # Unpack first operation.
        notation, *remaining = operation.upper().strip(' ').split(',')
        i = min(i for i, char in enumerate(notation) if char.isupper())
        prfx, face, sffx = notation[:i], notation[i], notation[i+1:]
        
        # Parse valid face, number of layers, and number of radions.
        if face not in self._face_axes:
            raise ValueError(f'Invalid operation face "{face}" in "{operation}"')
        if not prfx:
            layers = 1
            notation = f'1{notation}'
        elif prfx.isnumeric():
            layers = int(prfx)
        else:
            raise ValueError(f'Invalid operation prefix "{prfx}" in "{operation}"')
        if not sffx:
            rads = np.pi/2
            notation = f'{notation}1'
        elif sffx.isnumeric():
            rads = int(sffx)*np.pi/2
        else:
            raise ValueError(f'Invalid operation suffix "{sffx}" in "{operation}"')
        
        # Apply rotation to affected stickers.
        rotation = self._get_rotation(face=face, rads=rads)
        stickers = self._get_stickers(face=face, layers=layers)
        self._state.loc[stickers, self._axes] = self._state.loc[stickers, self._axes].dot(rotation)
        
        # Append rotation to history; recurse on remaining operations.
        self._history.append(notation)
        if remaining:
            self.rotate(operation=','.join(remaining))
    
    ###############################################################################################
    # COMPOSITIE OPERATIONS
    
    def scramble(self:object, n:int=100, turns:bool=False, layers:bool=False) -> str:
        '''
        ____________________________________________________________
        > Performs <n> random moves on the cube.
        
        Output:
            Comma-seperated sequence of applied rotations.
        ____________________________________________________________
        '''
        faces = np.random.choice(a=list(self._face_axes), size=n)
        if turns:
            array = np.random.randint(low=1, high=4, size=n)
            faces = [face+str(turn) for face, turn in zip(faces, array)]
        if layers:
            array = np.random.randint(low=1, high=self.dim+1, size=n)
            faces = [str(layer)+face for layer, face in zip(array, faces)]

        operation = ','.join(faces)
        self.rotate(operation=operation)
        return operation
        
    def unscramble(self:object) -> str:
        '''
        ____________________________________________________________
        > 'Solves' the cube by undoing rotations from initial solved state.
        
        Output:
            Comma-seperated sequence of applied rotations.
        ____________________________________________________________
        '''
        operation = ','.join(f'{move[:-1]}{-int(move[-1])%4}' for move in reversed(self._history))
        self.rotate(operation=operation)
        return operation
    
    ###############################################################################################
    # VISUALIZATION
    
    def _get_face(self:object) -> pd.Series:
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
        
    def _get_mesh(self:object) -> pd.DataFrame:
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
        mesh = self._get_mesh()
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
        
        # Append text-face trace.
        face = self._get_face()
        figure['data'].append({
            'type':'scatter3d', 'x':face['x'], 'y':face['y'], 'z':face['z'], 'text':face['text'],
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
        dbc.CardHeader([
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.InputGroupAddon(addon_type='prepend', children=[
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
                            id='rubik-button-clear',
                            children='Clear',
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
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

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
            # Clear cube.
            return [], []

        # Unpack arguments and enforce data types.
        *_, dim, scramble, state, history = args
        dim = int(dim)
        scramble = int(scramble)

        if trigger['prop_id'].endswith('load.n_clicks'):
            # Load new cube.
            cube = RubiksCube(dim=dim, state=None)
            return cube.get_state(), []
        cube = RubiksCube(dim=dim, state=state)

        if trigger['prop_id'].endswith('scramble.n_clicks'):
            # Scramble cube.
            operation = cube.scramble(n=scramble)
            history.extend({'move':move} for move in operation.split(','))
            return cube.get_state(), history

        if trigger['prop_id'].endswith('state.clickData'):
            # Rotate face of cube.
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
        ddp.Output('rubik-graph-state', 'figure'),
        [ddp.Input('rubik-store-state', 'data')],
        [ddp.State('rubik-select-dim', 'value')],
    )
    def graph_cube_state(state:list, dim:int) -> dict:
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