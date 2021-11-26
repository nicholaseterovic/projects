# Nicholas Eterovic 2021Q3
####################################################################################################

# Dash imports.
import dash
from dash import dcc
from dash import html as dhc
import dash_tabulator as dtb
import dash.dependencies as ddp
import dash_bootstrap_components as dbc

# In-house imports.
import constants

####################################################################################################
# LAYOUT

app_layout = [
    dbc.Row(
        class_name="g-0",
        style={"height":"100vh", "background-color":constants.NAVBAR_COLOR},
        children=[
            dbc.Col(width=7, children=[
                dbc.Card(style={"height":"100%", "border-radius":"0px"}, children=[
                    dbc.CardBody([
                        dcc.Markdown("""
                            # Home
                            ***

                            ### Introduction
                            ***

                              Greetings!
                              
                              You've stumbled upon my humble personal website,
                             home to some of my recreational math and coding projects.

                              Feel free to take a look at what's available using the sidebar.
                             For the best user experience, I recommend browsing with desktop Chrome.
                        """),
                        dcc.Markdown(style={"text-align":"right"}, children="""
                            *- Nick Eterovic*
                            ***
                        """),
                    ]),
                ]),
            ]),
            dbc.Col(width=5, children=[
                dhc.Img(
                    src="../assets/profile.jpg",
                    title="Boston, Fall of 2020",
                    style={"max-width":"100%", "max-height":"100vh"},
                ),
            ]),
        ],
    ),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:
    return