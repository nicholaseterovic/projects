# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import numpy as np
import pandas as pd
import typing as tp

# In-house packages.
from constants import constants

# Dash imports.
import dash
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

####################################################################################################
# LAYOUT

app_layout = [
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Room Dimensions:',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Length:',
                    ),
                    dbc.Input(
                        id='input-bug-room-length',
                        debounce=False,
                        value=1,
                        type='number',
                        min=0,
                        step=1,
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Width:',
                    ),
                    dbc.Input(
                        id='input-bug-room-width',
                        debounce=False,
                        value=1,
                        type='number',
                        min=0,
                        step=1,
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Height:',
                    ),
                    dbc.Input(
                        id='input-bug-room-height',
                        debounce=False,
                        value=1,
                        type='number',
                        min=0,
                        step=1,
                    ),
                    dbc.InputGroupAddon(
                        addon_type='append',
                        children=dbc.Button(
                            id='button-bug-room-confirm',
                            children='Confirm',
                            n_clicks=0,
                            color='primary',
                            disabled=False,
                        ),
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(width=6, children=[
                    dcc.Graph(
                        id='graph-bug-net',
                        figure=constants.empty_figure,
                        config={
                            'displayModeBar':False,
                            'displaylogo':False,
                            'editable':True,
                            'edits':{
                                'shapePosition':True,
                            },
                        },
                        style={
                            'height':'50vw',
                            'width':'50vw',
                        },
                    ),
                ]),
                dbc.Col(width=6, children=[
                    dcc.Graph(
                        id='graph-bug-room',
                        figure=constants.empty_figure,
                        config={
                            'displayModeBar':False,
                            'displaylogo':False,
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
            ddp.Output('button-bug-room-confirm', 'children'),
            ddp.Output('button-bug-room-confirm', 'color'),
            ddp.Output('button-bug-room-confirm', 'disabled'),
        ],
        [
            ddp.Input('input-bug-room-length', 'value'),
            ddp.Input('input-bug-room-width', 'value'),
            ddp.Input('input-bug-room-height', 'value'),
        ],
    )
    def validate_room_dimensions(*args:tp.List[int]) -> tp.Tuple[str, str, bool]:
        valid = all(isinstance(arg, int) and arg>0 for arg in args)
        if valid:
            return 'Confirm', 'primary', False
        return 'Confirm', 'warning', True

    @app.callback(
        ddp.Output('graph-bug-net', 'figure'),
        [ddp.Input('button-bug-room-confirm', 'n_clicks')],
        [
            ddp.State('input-bug-room-length', 'value'),
            ddp.State('input-bug-room-width', 'value'),
            ddp.State('input-bug-room-height', 'value'),
            ddp.State('graph-bug-net', 'figure'),
        ],
    )
    def populate_graph_net(n_clicks:int, x:int, y:int, z:int, figure:dict) -> dict:
        figure = {**constants.empty_figure, 'data':[]}
        if not all([x, y, z]):
            return figure
        
        figure['layout']['shapes'] = []
        figure['layout']['xaxis'].update({'fixedrange':True})
        figure['layout']['yaxis'].update({'fixedrange':True, 'scaleanchor':'x','scaleratio':1})
        
        # Draw the unpacked cuboid room as a net.
        faces = {
            'Floor':[(0, 0), (x, 0), (x, y), (0, y)],
            'Right Wall':[(x, 0), (x+z, 0), (x+z, y), (x, y)],
            'Left Wall':[(-z, 0), (0, 0), (0, y), (-z, y)],
            'Front Wall':[(0, y), (x, y), (x, y+z), (0, y+z)],
            'Back Wall':[(0, -z), (x, -z), (x, 0), (0, 0)],
            'Ceiling':[(x+z, 0), (x+z+x, 0), (x+x+z, y), (x+z, y)],
            'Ceiling (Duplicate)':[(0, -z-y), (x, -z-y), (x, -z), (0, -z)],
        }
        for desc, path in faces.items():
            figure['data'].append({
                'type':'scatter',
                'x':[x for x, y in path],
                'y':[y for x, y in path],
                'fill':'toself',
                'name':desc,
                'showlegend':False,
            })
        
        points = ['Bug', 'Lizard']
        for point in points:
            # Select a random face and (x, y) coordinate.
            face = 'Floor' if point=='Bug' else np.random.choice(list(faces.keys()))
            x = np.random.uniform(low=min(x for x, y in faces[face]), high=max(x for x, y in faces[face]))
            y = np.random.uniform(low=min(y for x, y in faces[face]), high=max(y for x, y in faces[face]))
            
            r = 0.1
            figure['layout']['shapes'].append({
                'layer':'above',
                'type':'circle',
                'editable':True,
                'opacity':0.75,
                'x0':x-r,
                'x1':x+r,
                'y0':y-r,
                'y1':y+r,
                'name':point,
                'fillcolor':'black' if point=='Bug' else 'green',
            })
        
        return figure