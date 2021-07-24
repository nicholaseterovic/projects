# Nicholas Eterovic 2020Q4
####################################################################################################

# Open-source Dash packages.
import dash
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as dhc
import dash_trich_components as dtc
import dash_bootstrap_components as dbc
import dash_extensions.javascript as djs

# Open-source miscellanous packages.
import numpy as np
import pandas as pd
import typing as tp
import sklearn.utils as sku

# In-house packages.
import utils.system as su

# In-house projects.
import kca.kca as kca
import home.home as home
import fractals.fractal as fractal
import rubiks_cube.rubiks_cube as rubiks_cube
import pivot_table.pivot_table as pivot_table
import game_of_life.game_of_life as game_of_life
import bug_and_lizard.bug_and_lizard as bug_and_lizard

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
    'home':{'label':'Home', 'icon':'fas fa-home', 'module':home},
    'cube':{'label':'Rubik\'s Cube', 'icon':'fas fa-cube', 'module':rubiks_cube},
    'pivot':{'label':'Pivot Table', 'icon':'fas fa-border-all', 'module':pivot_table},
    'fractal':{'label':'Fractal Generator', 'icon':'fas fa-snowflake', 'module':fractal},
    'bal':{'label':'The Bug and the Lizard', 'icon':'fas fa-bug', 'module':bug_and_lizard},
    'kca':{'label':'Kinetic Component Analysis', 'icon':'fas fa-chart-line', 'module':kca},
    'gol':{'label':'Conways\'s Game of Life', 'icon':'fas fa-braille', 'module':game_of_life},
}

links = {
    'github':{'icon':'fab fa-github', 'href':'https://github.com/NicholasEterovic'},
    'linkedin':{'icon':'fab fa-linkedin', 'href':'https://www.linkedin.com/in/nicholaseterovic'},
    'instagram':{'icon':'fab fa-instagram', 'href':'https://www.instagram.com/nicholaseterovic'},
}

app.layout = dhc.Div(
    style={'position':'relative'},
    children=[
        dtc.SideBar(
            bg_color='#2f4f4f',
            children=[
                dtc.SideBarItem(
                    id=f'sbi-{project}',
                    icon=params['icon'],
                    label=params['label'],
                )
                for project, params in projects.items()
            ] + [
                dhc.Hr(),
            ] + [
                dhc.Div(
                    style={'margin-left':'20px'},
                    children=[
                        dcc.Link(
                            target='_blank',
                            href=params['href'],
                            style={'margin-left':'20px'},
                            children=[
                                dtc.SideBarItem(
                                    icon=params['icon'],
                                    label='',
                                ),
                            ],
                        ),
                    ],
                )
                for link, params in links.items()
            ] + [
                dhc.Hr(),
            ],
        ),
        dhc.Div(id='page_content', style={'min-height':'100vh'}, children=[
            dcc.Tabs(
                id='tabs-projects',
                value=list(projects)[0],
                style={'height':'0px'},
                persistence=True,
                children=[
                    dcc.Tab(
                        value=project,
                        style={'line-height':'0px'},
                        children=[
                            dbc.NavbarSimple(
                                brand='Projects > '+params['label'],
                                brand_href=project,
                                color='#2f4f4f',
                                dark=True,
                                children=[],
                            ),
                            *getattr(params['module'], 'app_layout'),
                        ],
                    )
                    for project, params in projects.items()
                ],
            ),
        ],
    ),
])

####################################################################################################
# CALLBACKS

@app.callback(
    ddp.Output('tabs-projects', 'value'),
    [ddp.Input(f'sbi-{project}', 'n_clicks') for project in projects],
)
def click_tab(*_:tp.List[int]) -> str:
    trigger = dash.callback_context.triggered[0]
    return trigger['prop_id'].replace('sbi-', '').replace('.n_clicks', '')

for project, params in projects.items():
    if 'module' in params and hasattr(params['module'], 'register_app_callbacks'):
        getattr(params['module'], 'register_app_callbacks')(app=app)

####################################################################################################
# DEPLOY

if __name__ == '__main__':
    kwargs = su.get_cli_kwargs()
    app.run_server(**kwargs)
