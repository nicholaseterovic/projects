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
from constants import constants

# In-house projects.
import kca.kca as kca
import home.home as home
import fractals.fractal as fractal
import rubiks_cube.rubiks_cube as rubiks_cube
import pivot_table.pivot_table as pivot_table
import game_of_life.game_of_life as game_of_life
import bug_and_lizard.bug_and_lizard as bug_and_lizard
import boids.boid_simulation as boids

####################################################################################################
# APPLICATION

app = dash.Dash(
    name=__name__,
    title='Nicholas Eterovic',
    assets_folder='assets',
    prevent_initial_callbacks=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        # Font Awesome for icons.
        'https://use.fontawesome.com/releases/v5.15.0/css/all.css',
    ],
    external_scripts=[
        # Mathjax for formulae.
        'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML',
    ],
)
server = app.server
ns = djs.Namespace('dapp', 'tabulator')

####################################################################################################
# LAYOUT

links = {
    'github':{'icon':'fab fa-github', 'href':'https://github.com/NicholasEterovic'},
    'linkedin':{'icon':'fab fa-linkedin', 'href':'https://www.linkedin.com/in/nicholaseterovic'},
    'instagram':{'icon':'fab fa-instagram', 'href':'https://www.instagram.com/nicholaseterovic'},
}
projects = {
    'home':{'label':'Home', 'icon':'fas fa-home', 'module':home},
    'rubik':{'label':'Rubik\'s Cube', 'icon':'fas fa-cube', 'module':rubiks_cube},
    'pivot':{'label':'Pivot Table', 'icon':'fas fa-ruler-combined', 'module':pivot_table},
    'fractal':{'label':'Self-Similar Fractals', 'icon':'fas fa-wave-square', 'module':fractal},
    'bal':{'label':'The Bug and the Lizard', 'icon':'fas fa-bug', 'module':bug_and_lizard},
    'kca':{'label':'Kinetic Component Analysis', 'icon':'fas fa-chart-line', 'module':kca},
    'gol':{'label':'Conway\'s Game of Life', 'icon':'fas fa-heart', 'module':game_of_life},
    'boids':{'label':'Boids', 'icon':'fas fa-crow', 'module':boids},
}

app.layout = dhc.Div(
    style={'position':'relative'},
    children=[
        dtc.SideBar(
            bg_color=constants.bg_color,
            children=[
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
            ] + [
                dtc.SideBarItem(
                    id=f'sidebaritem-{project}',
                    icon=params['icon'],
                    label=params['label'],
                )
                for project, params in projects.items()
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
                persistence_type='local',
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
    [ddp.Input(f'sidebaritem-{project}', 'n_clicks') for project in projects],
)
def click_tab(*_:tp.List[int]) -> str:
    trigger = dash.callback_context.triggered[0]
    return trigger['prop_id'].replace('sidebaritem-', '').replace('.n_clicks', '')

for project, params in projects.items():
    if 'module' in params and hasattr(params['module'], 'register_app_callbacks'):
        getattr(params['module'], 'register_app_callbacks')(app=app)

####################################################################################################
# DEPLOY

if __name__ == '__main__':
    kwargs = su.get_cli_kwargs()
    app.run_server(**kwargs)
