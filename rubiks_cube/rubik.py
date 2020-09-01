# Nicholas Eterovic, 2020.

import pandas as pd
import itertools as it
import plotly.offline as py

class RubiksCube:
    
    ###############################################################################################
    # INITIALIZATION
    
    def __init__(self:object, dim:int=3) -> object:
        '''
        ____________________________________________________________
        > Instantiate a <dim>x<dim>x<dim> Rubik's cube in solved state.
        ____________________________________________________________
        '''
        self.dim = dim
        self._axes = ['x', 'y', 'z']
        self._colors = ['yellow', 'green', 'red', 'white', 'blue', 'orange']
        self._face_axes = {'L':'x-', 'R':'x+', 'U':'y+', 'D':'y-', 'F':'z+', 'B':'z-'}
        
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
        self._history = []
        return None
    
    ###############################################################################################
    # ATOMIC OPERATIONS
    
    def _get_stickers(self:object, face:str, layers:int) -> pd.Series:
        axis, sign = self._face_axes[face]
        return self._state[axis].mul(-1 if sign=='-' else +1).between(self.dim-2*layers, self.dim)
        
    def _get_rotation(self:object, face:str, rads:float) -> pd.DataFrame:
        # Unpack rotation axis and angle.
        axis, sign = self._face_axes[face]
        rads *= -1 if sign=='-' else +1
        
        # Construct 3D rotation matrix.
        cos, sin = pd.np.cos(rads), (-1 if axis=='y' else +1)*pd.np.sin(rads)
        rotation = pd.DataFrame(data=0, index=self._axes, columns=self._axes)
        rotation.loc[axis, axis] = 1
        rotation.loc[rotation.index.difference([axis]), rotation.columns.difference([axis])] = [
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
        operation='2T3' rotates the top-face top-two-layers by 90-degrees clockwise.
        ____________________________________________________________
        '''
        if not operation:
            return self
        
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
            rads = pd.np.pi/2
            notation = f'{notation}1'
        elif sffx.isnumeric():
            rads = int(sffx)*pd.np.pi/2
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
    
    def scramble(self:object, n:int=100) -> str:
        '''
        ____________________________________________________________
        > Performs <n> random moves on the cube.
        
        Output:
            Comma-seperated sequence of applied rotations.
        ____________________________________________________________
        '''
        faces = pd.np.random.choice(a=list(self._face_axes), size=moves)
        turns = pd.np.random.randint(low=1, high=4, size=moves)
        layers = pd.np.random.randint(low=1, high=self.dim+1, size=moves)
        operation = ','.join(f'{layer}{face}{turn}' for face, turn, layer in zip(faces, turns, layers))
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
                **{axis:(self.dim+1)*(-1 if '-' in desc else +1)*int(axis in desc) for axis in self._axes},
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
                    'hoverinfo':'skip', 'legendgroup':'frame', 'showlegend':i==j==0,
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
            'type':'mesh3d', 'x':x, 'y':y, 'z':z, 'facecolor':mesh['color'], 'hoverinfo':'skip',
            **{
                v:mesh[[f'{v}x', f'{v}y', f'{v}z']].apply(lambda row:xyz.index(tuple(row)), axis=1)
                for v in ['i', 'j', 'k']
            },
        })
        
        # Append text-face trace.
        face = self._get_face()
        figure['data'].append({
            'type':'scatter3d', 'x':face['x'], 'y':face['y'], 'z':face['z'], 'text':face['text'],
            'mode':'text', 'textposition':'middle center', 'hoverinfo':'skip', 'name':'Faces', 'textfont':{'size':30},
        })
        
        return figure