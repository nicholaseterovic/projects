# Nicholas Eterovic 2020Q4
####################################################################################################

# Open-source Dash packages.
import dash
import dash_canvas as dcv
import dash_tabulator as dtb
import dash_pivottable as dpv
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as dhc
import dash_trich_components as dtc
import dash_bootstrap_components as dbc
import dash_extensions.javascript as djs

# Open-source miscellanous packages.
import os
import json
import math
import numpy as np
import pandas as pd
import typing as tp
import pykalman as pk
import plotly.data as ptd
import plotly.colors as pcl
import sklearn.utils as sku
import plotly.subplots as psp
import sklearn.datasets as skd

# In-house packages.
import util.system as su
from fractals.fractal import Fractal
from rubiks_cube.rubik import RubiksCube

####################################################################################################
# APPLICATION
app = dash.Dash(
    name=__name__,
    title='Nicholas Eterovic',
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=False,
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
    'bug':{'label':'The Bug and the Lizard', 'icon':'fas fa-bug'},
    'kca':{'label':'Kinetic Component Analysis', 'icon':'fas fa-chart-line'},
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
                    (0.1, 0.9, '<b>Mouse-wheel</b><br>to zoom in and out'),
                    (0.9, 0.9, '<b>Left-click and drag</b><br>(outside the cube)<br>to rotate the cube'),
                    (0.1, 0.1, '<b>Left-click on a cube face</b><br>to rotate by 90º clockwise'),
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
            persistence=True,
            children=[
                dcc.Tab(
                    value='home',
                    style={'line-height':'0px'},
                    children=[
                        dbc.NavbarSimple(
                            brand='Projects > '+projects['home']['label'],
                            brand_href='home',
                            color='#2f4f4f',
                            dark=True,
                            children=[],
                        ),
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
                        dbc.NavbarSimple(
                            brand='Projects > '+projects['cube']['label'],
                            brand_href='cube',
                            color='#2f4f4f',
                            dark=True,
                            children=[],
                        ),
                        dcc.Store(id='rubik-store-state', data=None),
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
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col(width=10, children=[
                                        dcc.Graph(
                                            id='rubik-graph-state',
                                            style={'height':'100vh', 'border':'1px black solid'},
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
                    ],
                ),
                dcc.Tab(
                    value='pivot',
                    style={'line-height':'0px'},
                    children=[
                        dbc.NavbarSimple(
                            brand='Projects > '+projects['pivot']['label'],
                            brand_href='pivot',
                            color='#2f4f4f',
                            dark=True,
                            children=[],
                        ),
                        dbc.Card([
                            dbc.CardHeader([
                                dbc.InputGroup(
                                    size='sm',
                                    children=[
                                        dbc.DropdownMenu(
                                            label='Load',
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
                            ]),
                            dbc.CardBody([
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
                            ]),
                        ]),
                        dbc.Card([
                            dbc.CardBody([
                                dhc.Div(id='pivot-div-agg', children=[]),
                            ]),
                        ]),
                    ],
                ),
                dcc.Tab(
                    value='fractal',
                    style={'line-height':'0px'},
                    children=[
                        dbc.NavbarSimple(
                            brand='Projects > '+projects['fractal']['label'],
                            brand_href='fractal',
                            color='#2f4f4f',
                            dark=True,
                            children=[],
                        ),
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
                                            figure=empty_figure,
                                        ),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ],
                ),
                dcc.Tab(
                    value='bug',
                    style={'line-height':'0px'},
                    children=[
                        dbc.NavbarSimple(
                            brand='Projects > '+projects['bug']['label'],
                            brand_href='bug',
                            color='#2f4f4f',
                            dark=True,
                            children=[],
                        ),
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
                                            figure=empty_figure,
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
                                            figure=empty_figure,
                                            config={
                                                'displayModeBar':False,
                                                'displaylogo':False,
                                            },
                                        ),
                                    ]),
                                ]),
                            ]),
                            dbc.CardFooter([
                                
                            ]),
                        ]),
                    ],
                ),
                dcc.Tab(
                    value='kca',
                    children=[
                        dbc.NavbarSimple(
                            brand='Projects > '+projects['kca']['label'],
                            brand_href='kca',
                            color='#2f4f4f',
                            dark=True,
                            children=[],
                        ),
                        dcc.Store(id='store-kca-bars', data=[]),
                        dbc.Card([
                            dbc.CardHeader([
                                dbc.InputGroup(
                                    size='sm',
                                    children=[
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children=dbc.Button(
                                                children='VWAP Data',
                                                n_clicks=0,
                                                color='dark',
                                                disabled=True,
                                            ),
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children='Trade Data:',
                                        ),
                                        dbc.Select(
                                            id='select-kca-data-path',
                                            options=[
                                                {'label':file, 'value':os.path.join('data', 'futures', file)}
                                                for file in reversed(sorted(os.listdir(os.path.join('data', 'futures'))))
                                                if file.endswith('trd2.gz')
                                            ],
                                            value=None,
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children='Volume per Bar:',
                                        ),
                                        dbc.Input(
                                            id='input-kca-bars-delv',
                                            debounce=False,
                                            value=100,
                                            type='number',
                                            min=1,
                                            step=1,
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children='View Analysis In:',
                                        ),
                                        dbc.Select(
                                            id='select-kca-bars-time',
                                            options=[
                                                {'label':'Volume Time', 'value':'VBAR'},
                                                {'label':'Chronological Time', 'value':'TIMESTAMP_last'},
                                            ],
                                            value='VBAR',
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='append',
                                            children=dbc.Button(
                                                id='button-kca-bars-load',
                                                children='Load',
                                                n_clicks=0,
                                                color='primary',
                                                disabled=True,
                                            ),
                                        ),
                                    ],
                                ),
                            ]),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col(width=6, children=[
                                        dcc.Graph(
                                            id='graph-kca-bars-vwap',
                                            config={'displayModeBar':False, 'displaylogo':False},
                                            figure=psp.make_subplots(
                                                rows=1,
                                                cols=2,
                                                shared_yaxes=False,
                                                column_widths=[2/3, 1/3],
                                                x_title='Time',
                                                y_title='VWAP',
                                                subplot_titles=[
                                                    'Volume-Weighted-Average-Price (VWAP) by Time',
                                                    'Distribution',
                                                ],
                                            ),
                                        ),
                                    ]),
                                    dbc.Col(width=6, children=[
                                        dcc.Graph(
                                            id='graph-kca-bars-volume',
                                            config={'displayModeBar':False, 'displaylogo':False},
                                            figure=psp.make_subplots(
                                                rows=1,
                                                cols=2,
                                                shared_yaxes=False,
                                                column_widths=[2/3, 1/3],
                                                horizontal_spacing=0.05,
                                                x_title='Time',
                                                y_title='Volume',
                                                subplot_titles=[
                                                    'Volume by Time',
                                                    'Distribution',
                                                ],
                                            ),
                                        ),
                                    ]),
                                ]),
                            ]),
                        ]),
                        dcc.Store(id='store-kca-filt', data={}),
                        dbc.Card([
                            dbc.CardHeader([
                                dbc.InputGroup(
                                    size='sm',
                                    children=[
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children=dbc.Button(
                                                children='KCA Model',
                                                n_clicks=0,
                                                color='dark',
                                                disabled=True,
                                            ),
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children='Degree:',
                                        ),
                                        dbc.Input(
                                            id='input-kca-filt-pow',
                                            debounce=False,
                                            value=2,
                                            type='number',
                                            min=0,
                                            max=3,
                                            step=1,
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children='State Covariance Seed:',
                                        ),
                                        dbc.Input(
                                            id='input-kca-filt-seed',
                                            debounce=False,
                                            value=1e-3,
                                            type='number',
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='prepend',
                                            children='EM Iterations:',
                                        ),
                                        dbc.Input(
                                            id='input-kca-filt-iter',
                                            debounce=False,
                                            value=1,
                                            type='number',
                                            min=1,
                                            step=1,
                                        ),
                                        dbc.InputGroupAddon(
                                            addon_type='append',
                                            children=dbc.Button(
                                                id='button-kca-filt-fit',
                                                children='Fit',
                                                n_clicks=0,
                                                color='primary',
                                                disabled=True,
                                            ),
                                        ),
                                    ],
                                ),
                            ]),
                            dbc.CardBody([
                                dbc.Textarea(
                                    id='textarea-kca-filt',
                                    value='',
                                    placeholder='Trade Data Required',
                                    spellCheck=False,
                                    bs_size='sm',
                                    disabled=True,
                                    style={'height':'50vh'},
                                ),
                            ]),
                        ]),
                        dbc.Card([
                            dbc.CardHeader([
                                'State Estimate Analysis',
                            ]),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='graph-kca-smooth',
                                    config={'displayModeBar':False, 'displaylogo':False},
                                    figure=psp.make_subplots(
                                        rows=1,
                                        cols=2,
                                        shared_yaxes=False,
                                        column_widths=[2/3, 1/3],
                                        x_title='Time',
                                        y_title='Smoothed State',
                                        subplot_titles=[
                                            'Smoothed States by Time',
                                            'Distribution',
                                        ],
                                    ),
                                ),
                                dcc.Graph(
                                    id='graph-kca-filter',
                                    config={'displayModeBar':False, 'displaylogo':False},
                                    figure=psp.make_subplots(
                                        rows=1,
                                        cols=2,
                                        shared_yaxes=False,
                                        column_widths=[2/3, 1/3],
                                        x_title='Time',
                                        y_title='Filtered State',
                                        subplot_titles=[
                                            'Filtered States by Time',
                                            'Distribution',
                                        ],
                                    ),
                                ),
                                dcc.Graph(
                                    id='graph-kca-pred',
                                    config={'displayModeBar':False, 'displaylogo':False},
                                    figure=psp.make_subplots(
                                        rows=1,
                                        cols=2,
                                        shared_yaxes=False,
                                        column_widths=[2/3, 1/3],
                                        x_title='Time',
                                        y_title='Predicted State',
                                        subplot_titles=[
                                            'Predicted States by Time',
                                            'Distribution',
                                        ],
                                    ),
                                ),
                            ]),
                        ]),
                        dbc.Card([
                            dbc.CardHeader([
                                'VWAP Prediction Analysis',
                            ]),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col(width=8, children=[
                                        dcc.Graph(
                                            id='graph-kca-error-cae',
                                            config={'displayModeBar':False, 'displaylogo':False},
                                            figure={
                                                'data':{},
                                                'layout':{
                                                    'title':'Cumulative Absolute Error',
                                                    'yaxis':{'title':'CAE'},
                                                    'xaxis':{'title':'Time'},
                                                },
                                            },
                                        ),
                                    ]),
                                    dbc.Col(width=4, children=[
                                        dcc.Graph(
                                            id='graph-kca-error-dist',
                                            config={'displayModeBar':False, 'displaylogo':False},
                                            figure={
                                                'data':{},
                                                'layout':{
                                                    'title':'Error Distribution',
                                                    'yaxis':{'title':'Error Bin Count'},
                                                    'xaxis':{'title':'Error Bin'},
                                                    'barmode':'overlay',
                                                },
                                            },
                                        ),
                                    ]),
                                ]),
                            ]),
                        ]),
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
        raise dex.PreventUpdate
    
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
    ddp.Output('fractal-graph-iterations', 'figure'),
    [ddp.Input('fractal-store-iterations', 'data')],
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
# THE BUG AND THE ROOM

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
    figure = {**empty_figure, 'data':[]}
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

####################################################################################################
# KINETIC COMPONENT ANALYSIS

@app.callback(
    [
        ddp.Output('button-kca-bars-load', 'children'),
        ddp.Output('button-kca-bars-load', 'color'),
        ddp.Output('button-kca-bars-load', 'disabled'),
    ],
    [
        ddp.Input('select-kca-data-path', 'value'),
        ddp.Input('input-kca-bars-delv', 'value'),
        ddp.Input('select-kca-bars-time', 'value'),
    ],
)
def set_load_state(path:str, delv:int, time:str) -> tp.Tuple[str, str, bool]:
    if not path or not delv or not time or not os.path.isfile(path=path) or not isinstance(delv, int):
        return 'Load', 'primary', True
    return 'Load', 'primary', False

@app.callback(
    [
        ddp.Output('store-kca-bars', 'data'),
        ddp.Output('graph-kca-bars-vwap', 'figure'),
        ddp.Output('graph-kca-bars-volume', 'figure'),
    ],
    [ddp.Input('button-kca-bars-load', 'n_clicks')],
    [
        ddp.State('select-kca-data-path', 'value'),
        ddp.State('input-kca-bars-delv', 'value'),
        ddp.State('select-kca-bars-time', 'value'),
        ddp.State('graph-kca-bars-vwap', 'figure'),
        ddp.State('graph-kca-bars-volume', 'figure'),
    ],
)
def load_data(n_clicks:int, path:str, delv:str, time:str, *figures:tp.List[dict]) -> tp.List[dict]:
    if not n_clicks:
        raise dex.PreventUpdate
    for figure in figures:
        figure.update({'data':[]})
    if not path or not delv or not time or not os.path.isfile(path=path) or not isinstance(delv, int):
        return ([], *figures)
    try:
        # Load clean futures trade data.
        file = os.path.basename(path)
        code = file.split(sep='.')[0]
        data = pd.read_csv(filepath_or_buffer=path, usecols=['TIMESTAMP', 'PRICE', 'SIZE'])
        data = data.loc[data['TIMESTAMP'].ne(f'DATA_QUALITY_CHANGE:{code}')]
        # Enforce data types.
        data['PRICE'] = data['PRICE'].astype(float)
        data['SIZE'] = data['SIZE'].astype(int)
        data['TIMESTAMP'] = pd.to_datetime(arg=data['TIMESTAMP'].astype(str), format='%Y%m%d%H%M%S.%f')
        # Resample trade data into volume bars.
        by = data['SIZE'].cumsum().floordiv(delv).mul(delv).rename('VBAR')
        func = {'TIMESTAMP':['first', 'last'], 'NOTIONAL':'sum', 'SIZE':'sum'}
        data['NOTIONAL'] = data['PRICE']*data['SIZE']
        bars = data.groupby(by=by).agg(func=func)
        bars.columns = bars.columns.map('_'.join)
        bars.reset_index(level='VBAR', drop=False, inplace=True)
        bars['VWAP'] = bars['NOTIONAL_sum']/bars['SIZE_sum']
        # Return volume-bar records.
        records = bars.to_dict(orient='records')
        colors = pcl.DEFAULT_PLOTLY_COLORS
        for i, (col, figure) in enumerate(zip(['VWAP', 'SIZE_sum'], figures)):
            # Reset layout.
            figure['layout'].update({'template':None})
            for axis in ('xaxis', 'yaxis'):
                for key in ('type', 'range', 'autorange'):
                    figure['layout'][axis].pop(key, None)
            # Renew data.
            color = colors[i%len(colors)]
            figure.update({'data':[
                {
                    'type':'scatter',
                    'y':bars[col],
                    'x':bars[time],
                    'xaxis':'x',
                    'yaxis':'y',
                    'name':col.split('_')[0],
                    'legendgroup':col,
                    'showlegend':True,
                    'connectgaps':False,
                    'line':{'color':color},
                },
                {
                    'type':'box',
                    'y':bars[col],
                    'xaxis':'x2',
                    'yaxis':'y2',
                    'name':col.split('_')[0],
                    'legendgroup':col,
                    'showlegend':False,
                    'boxmean':'sd',
                    'boxpoints':False,
                    'line':{'color':color},
                    'marker':{'color':color},
                },
            ]})
            

        return (records, *figures)
    except Exception as exception:
        print(str(exception))
        return ([], *figures)

@app.callback(
    [
        ddp.Output('button-kca-filt-fit', 'children'),
        ddp.Output('button-kca-filt-fit', 'color'),
        ddp.Output('button-kca-filt-fit', 'disabled'),
    ],
    [
        ddp.Input('store-kca-bars', 'data'),
        ddp.Input('input-kca-filt-pow', 'value'),
        ddp.Input('input-kca-filt-seed', 'value'),
        ddp.Input('input-kca-filt-iter', 'value'),
    ],
)
def set_fit_state(records:tp.List[dict], pow:int, seed:float, iter:str) -> tp.Tuple[str, str, bool]:
    if not all([records, seed, iter]) or not isinstance(pow, int) or not isinstance(iter, int):
        return 'Fit', 'primary', True
    return 'Fit', 'primary', False

@app.callback(
    [
        ddp.Output('store-kca-filt', 'data'),
        ddp.Output('textarea-kca-filt', 'value'),
    ],
    [ddp.Input('button-kca-filt-fit', 'n_clicks')],
    [
        ddp.State('store-kca-bars', 'data'),
        ddp.State('select-kca-bars-time', 'value'),
        ddp.State('input-kca-filt-pow', 'value'),
        ddp.State('input-kca-filt-seed', 'value'),
        ddp.State('input-kca-filt-iter', 'value'),
    ],
)
def fit_filt(n_clicks:int, records:tp.List[dict], time:str, pow:int, seed:float, iter:int, *figures:tp.List[dict]) -> dict:
    if not n_clicks:
        raise dex.PreventUpdate
    if not all([records, seed, iter]) or not isinstance(pow, int) or not isinstance(iter, int):
        return {}, ''
    try:
        # Retrieve VWAP and VBAR data.
        bars = pd.DataFrame(data=records)
        dv = bars['SIZE_sum'].mean()
        X = bars[['VWAP']]
        # Specify Kalman Filter model.
        states = range(pow+1)
        A = [[0 if i>j else dv**(j-i)/math.factorial(j-i) for j in states] for i in states]
        C = [[1 if i==0 else 0 for i in states]]
        Q = [[0 if i!=j else seed**i if seed<0 else seed**-i if i==j else 0 for j in states] for i in states]
        z = [X.iloc[0, 0] if i==0 else 0 for i in states]
        em_vars = ['transition_covariance', 'observation_covariance']
        kf = pk.KalmanFilter(
            transition_matrices=A,
            transition_covariance=None,
            observation_matrices=C,
            observation_covariance=None,
            initial_state_mean=z,
            initial_state_covariance=Q,
            em_vars=em_vars,
        )
        # Apply Expectation Maximization to estimate remaining parameters.
        kf.em(X=X, n_iter=iter, em_vars=em_vars)
        # Extrat model specification.
        text = json.dumps(obj=kf.__dict__, indent=4, default=lambda x:list(x) if pd.api.types.is_list_like(x) else float(x))
        filt = json.loads(s=text)
        return (filt, text, *figures)
    except Exception as exception:
        print(str(exception))
        return {}, ''

@app.callback(
    [
        ddp.Output('graph-kca-smooth', 'figure'),
        ddp.Output('graph-kca-filter', 'figure'),
        ddp.Output('graph-kca-pred', 'figure'),
    ],
    [ddp.Input('store-kca-filt', 'data')],
    [
        ddp.State('store-kca-bars', 'data'),
        ddp.State('select-kca-bars-time', 'value'),
        ddp.State('graph-kca-smooth', 'figure'),
        ddp.State('graph-kca-filter', 'figure'),
        ddp.State('graph-kca-pred', 'figure'),
    ],
)
def plot_filt(cfg:dict, records:tp.List[dict], time:str, *figures:tp.List[dict]) -> dict:
    if not cfg:
        raise dex.PreventUpdate
    for figure in figures:
        figure.update({'data':[]})
    if not all([records, time]):
        return figures
    try:
        # Retrieve VWAP and VBAR data.
        bars = pd.DataFrame(data=records)
        X = bars[['VWAP']]
        # Specify Kalman Filter model.
        kf = pk.KalmanFilter(**cfg)
        # Clean figures.
        colors = pcl.DEFAULT_PLOTLY_COLORS
        for figure in figures:
            # Reset layout.
            figure['layout'].update({'template':None})
            for axis in ('xaxis', 'yaxis'):
                for key in ('type', 'range', 'autorange'):
                    figure['layout'][axis].pop(key, None)
            # Renew data.
            color = colors[0]
            figure.update({'data':[
                {
                    'type':'scatter',
                    'y':bars['VWAP'],
                    'x':bars[time],
                    'xaxis':'x',
                    'yaxis':'y',
                    'name':'Observed VWAP',
                    'legendgroup':'VWAP',
                    'showlegend':True,
                    'connectgaps':False,
                    'line':{'color':color},
                    'hoverlabel':{'namelength':-1},
                },
                {
                    'type':'box',
                    'y':bars['VWAP'],
                    'xaxis':'x2',
                    'yaxis':'y2',
                    'name':'Observed VWAP',
                    'legendgroup':'VWAP',
                    'showlegend':False,
                    'boxmean':'sd',
                    'boxpoints':False,
                    'line':{'color':color},
                    'marker':{'color':color},
                    'hoverlabel':{'namelength':-1},
                },
            ]})
        # Construct smoothed state figures.
        Z, V = kf.smooth(X=X)
        V = np.array(list(map(np.diag, V)))
        for i, (z, v) in enumerate(zip(Z.T, V.T)):
            color = colors[(i+1)%len(colors)]
            figures[0]['data'].extend([
                {
                    'type':'scatter',
                    'fill':'tonexty',
                    'y':z+dev*v**.5,
                    'x':bars[time],
                    'xaxis':'x',
                    'yaxis':'y',
                    'name':f'Smoothed Degree {i} (M{dev:+.0f}SD)',
                    'legendgroup':i,
                    'showlegend':dev==0,
                    'visible':True if i==0 else 'legendonly',
                    'connectgaps':False,
                    'line':{'color':color},
                    'hoverlabel':{'namelength':-1},
                }
                for dev in (-1, 0, 1)
            ] + [
                {
                    'type':'box',
                    'y':z,
                    'xaxis':'x2',
                    'yaxis':'y2',
                    'name':f'Smoothed Degree {i}',
                    'legendgroup':i,
                    'showlegend':False,
                    'visible':True if i==0 else 'legendonly',
                    'boxmean':'sd',
                    'boxpoints':False,
                    'line':{'color':color},
                    'marker':{'color':color},
                    'hoverlabel':{'namelength':-1},
                },
            ])
        # Construct filtered state figures.
        Z, V = kf.filter(X=X)
        V = np.array(list(map(np.diag, V)))
        for i, (z, v) in enumerate(zip(Z.T, V.T)):
            color = colors[(i+1)%len(colors)]
            figures[1]['data'].extend([
                {
                    'type':'scatter',
                    'fill':'tonexty',
                    'y':z+dev*v**.5,
                    'x':bars[time],
                    'xaxis':'x',
                    'yaxis':'y',
                    'name':f'Filtered Degree {i} (M{dev:+.0f}SD)',
                    'legendgroup':i,
                    'showlegend':dev==0,
                    'visible':True if i==0 else 'legendonly',
                    'connectgaps':False,
                    'line':{'color':color},
                    'hoverlabel':{'namelength':-1},
                }
                for dev in (-1, 0, +1)
            ] + [
                {
                    'type':'box',
                    'y':z,
                    'xaxis':'x2',
                    'yaxis':'y2',
                    'name':f'Filtered Degree {i}',
                    'legendgroup':i,
                    'showlegend':False,
                    'visible':True if i==0 else 'legendonly',
                    'boxmean':'sd',
                    'boxpoints':False,
                    'line':{'color':color},
                    'marker':{'color':color},
                    'hoverlabel':{'namelength':-1},
                },
            ])
        # Construct predicted state figures.
        A = np.array(kf.transition_matrices)
        Z = np.array(list(map(A.dot, Z)))
        for i, (z, v) in enumerate(zip(Z.T, V.T)):
            color = colors[(i+1)%len(colors)]
            figures[2]['data'].extend([
                {
                    'type':'scatter',
                    'fill':'tonexty',
                    'y':z+dev*v**.5,
                    'x':bars[time],
                    'xaxis':'x',
                    'yaxis':'y',
                    'name':f'Predicted Degree {i} (M{dev:+.0f}SD)',
                    'legendgroup':i,
                    'showlegend':dev==0,
                    'visible':True if i==0 else 'legendonly',
                    'connectgaps':False,
                    'line':{'color':color},
                    'hoverlabel':{'namelength':-1},
                }
                for dev in (-1, 0, 1)
            ] + [
                {
                    'type':'box',
                    'y':z,
                    'xaxis':'x2',
                    'yaxis':'y2',
                    'name':f'Predicted Degree {i}',
                    'legendgroup':i,
                    'showlegend':False,
                    'visible':True if i==0 else 'legendonly',
                    'boxmean':'sd',
                    'boxpoints':False,
                    'line':{'color':color},
                    'marker':{'color':color},
                    'hoverlabel':{'namelength':-1},
                },
            ])
        return figures
    except Exception as exception:
        print(str(exception))
        return figures

@app.callback(
    [
        ddp.Output('graph-kca-error-cae', 'figure'),
        ddp.Output('graph-kca-error-dist', 'figure'),
    ],
    [ddp.Input('graph-kca-pred', 'figure')],
    [
        ddp.State('graph-kca-error-cae', 'figure'),
        ddp.State('graph-kca-error-dist', 'figure'),
    ],
)
def load_error(pred:dict, *figures:tp.List[dict]) -> dict:
    pred.setdefault('data', [])
    for figure in figures:
        figure.update({'data':[]})
    vwap = [datum for datum in pred['data'] if datum['legendgroup']=='VWAP']
    pred = [datum for datum in pred['data'] if datum['legendgroup']==0 and '0' in datum['name']]
    if not vwap or not pred:
        return figures
    figures[0]['data'].extend([
        {
            'type':'scatter',
            'x':vwap[0]['x'][1:],
            'y':np.cumsum(np.abs(np.subtract(vwap[0]['y'][:-1], vwap[0]['y'][1:]))),
            'name':'Martingale Prediction (Benchmark)',
            'hoverlabel':{'namelength':-1},
            'fill':'tozeroy',
        },
        {
            'type':'scatter',
            'x':vwap[0]['x'][1:],
            'y':np.cumsum(np.abs(np.subtract(pred[0]['y'][1:], vwap[0]['y'][1:]))),
            'name':pred[0]['name'],
            'hoverlabel':{'namelength':-1},
            'fill':'tozeroy',
        },
    ])
    figures[1]['data'].extend([
        {
            'type':'histogram',
            'x':np.subtract(vwap[0]['y'][:-1], vwap[0]['y'][1:]),
            'name':'Martingale Prediction (Benchmark)',
            'hoverlabel':{'namelength':-1},
            'opacity':0.5,
        },
        {
            'type':'histogram',
            'x':np.subtract(pred[0]['y'][1:], vwap[0]['y'][1:]),
            'name':pred[0]['name'],
            'hoverlabel':{'namelength':-1},
            'opacity':0.5,
        },
    ])
    return figures

####################################################################################################
# DEPLOY

if __name__ == '__main__':
    kwargs = su.get_cli_kwargs()
    app.run_server(**kwargs)