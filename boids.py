# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import numpy as np
import pandas as pd
import typing as tp
import itertools as it

# Dash imports.
import dash
from dash import dcc
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_bootstrap_components as dbc

####################################################################################################

class BoidSimulation(object):
    
    _dims = 2,

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
        """
        > Initialize an iterator that yields iterations of a Boid simulation. 
        
        Arguments:
            state: Dataframe with columns "px", "py, ..., "vx", "vy", ... encoding initial Boids.
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
        """
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
        self._dims:tp.List[str] = ["x", "y"]
        self._N:int = self.time//self.step
        self._n:int = 0

    def __iter__(self) -> object:
        return self
    
    def __next__(self) -> pd.DataFrame:
        """
        > Return the next iteration of the Boid simulation.
        
        Arguments:
            None
        Returns:
            List-of-pairs [(x, y), ...] coordinates of next live cells. 
        """
        if self._n  >= self._N:
            raise StopIteration
        state = BoidSimulation._get_next_state(
            state=self.state,
            seperation=self.seperation,
            cohesion=self.cohesion,
            alignment=self.alignment,
            visibility=self.visibility,
            dimensions=self._dims,
            step=self.step,
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
        step:float,
    ) -> pd.DataFrame:

        # Self-cross-product Boids for all (center, neighbor) pairs.
        state["i"] = range(len(state))
        state["j"] = 0
        pairs = pd.merge(
            left=state,
            right=state.add_prefix(prefix="n"),
            left_on="j",
            right_on="nj",
            how="outer",
        )

        # Unpack columns.
        cols = [
            (
                f"p{i}", # Positions
                f"v{i}", # Velocitys
                f"np{i}", # Neighbor positions.
                f"nv{i}", # Neighbor velocitys.
                f"nd{i}", # Neighbor distances.
            )
            for i in dimensions
        ]
        p, v, np, nv, nd = map(list, zip(*cols))
        
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

        # Nullify neighbors that are centers.
        pairs.loc[pairs["i"]==pairs["ni"], [*np, *nv, *nd]] = None
        
        # Augment repulsor behaviour.
        centers = pairs["t"].eq("repulsor")
        pairs.loc[centers, np] = None
        pairs.loc[centers, nv] = None
        pairs.loc[centers, nd] = None
        neighbors = pairs["nt"].eq("repulsor")
        pairs.loc[neighbors, np] = None
        pairs.loc[neighbors, nv] = None
        pairs.loc[neighbors, nd] *= 30

        # Aggregate neighbor information per center Boid.
        agg_last = {col:"last" for col in ("t", *p, *v)}
        agg_mean = {col:"mean" for col in (*np, *nv, *nd)}
        agg = {**agg_last, **agg_mean}
        groups = pairs.groupby(by="i", as_index=False, sort=False)
        state = groups.agg(func=agg).drop(columns="i")

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
            state[vi] += ai * step**2
            state[pi] += state[vi] * step

        return state

    @staticmethod
    def get_random_boids_state(num_boids:int=100, loc:float=0, scale:float=1) -> pd.DataFrame:
        dims = 2
        data = np.random.normal(size=(num_boids, dims), loc=loc, scale=scale)
        state = pd.DataFrame(data=data, columns=["px", "py"])
        state["vx"] = 0
        state["vy"] = 0
        state["t"] = "boid"
        return state

    @staticmethod
    def get_circle_repulsor_state(num_repulsors:int=100, loc:float=0, radius:float=1) -> pd.DataFrame:
        dims = 2
        theta = np.linspace(start=0, stop=2*np.pi, num=num_repulsors, endpoint=False)
        x = radius*np.cos(theta)
        y = radius*np.sin(theta)
        state = pd.DataFrame({"px":x, "py":y})
        state["vx"] = 0
        state["vy"] = 0
        state["t"] = "repulsor"
        return state

####################################################################################################
# LAYOUT

empty_boids_figure = {
    "data":[],
    "frames":[],
    "layout":{
        "dragmode":False,
        "hovermode":"closest",
        "xaxis":{"range":[-10, 10], "autorange":False},
        "yaxis":{"range":[-10, 10], "autorange":False, "scaleanchor":"x"},
        "updatemenus":[
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
        "sliders":[
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
        dbc.CardBody([
            dcc.Markdown("""
                # Who Let the Boids Out?
                ***

                ### Introduction
                ***

                  This project originated in the Summer of 2020
                with a sudden motivation to learn how to solve a **Rubik"s cube**.
                Little did I know of how deep the cubing rabbit"s hole goes!

                  As I sat fiddling and memorizing the various algorithms needed to assemble colors,
                I decided that a better way to learn the cube"s intricacies was instead to *code it up*.

                  The result is a *virtual cube* that I am proud to share with you.
                If you are curious,
                I have documented below my modelling and implementation approach.
            """),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size="sm",
                children=[
                    dbc.Button(
                        id="button-boids-reset",
                        children="Reset",
                        n_clicks=0,
                        color="primary",
                        disabled=False,
                    ),
                    dbc.InputGroupText("Seperation:"),
                    dbc.Input(
                        id="input-boids-seperation",
                        min=0,
                        placeholder="<Non-negative number>",
                        value=1,
                        disabled=False,
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dcc.Graph(
                id="graph-boids-sim",
                config={"displayModeBar":False, "displaylogo":False},
                figure=empty_boids_figure,
                style={"height":"80vh"},
            ),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        ddp.Output("button-boids-reset", "n_clicks"),
        [ddp.Input("tabs-projects", "value")],
        [ddp.State("button-boids-reset", "n_clicks")],
    )
    def click_reset(tab:str, n_clicks:int) -> int:
        if tab != "boids" or n_clicks > 0:
            raise dex.PreventUpdate
        return n_clicks + 1

    @app.callback(
        ddp.Output("graph-boids-sim", "figure"),
        [ddp.Input("button-boids-reset", "n_clicks")],
        [ddp.State("graph-boids-sim", "figure")]
    )
    def reset_graph(n_clicks:int, figure:dict) -> dict:
        
        dt = 0.3
        duration = 1000*dt

        ranges = (figure["layout"][axis]["range"] for axis in ["xaxis", "yaxis"])
        diameters = map(lambda range:range[-1]-range[0], ranges)
        radius = 0.5*min(diameters)

        initial_boids = BoidSimulation.get_random_boids_state(num_boids=50, scale=0.5)
        initial_repulsors = BoidSimulation.get_circle_repulsor_state(num_repulsors=100, radius=radius)
        initial_state = pd.concat(ignore_index=True, objs=[
            initial_boids,
            initial_repulsors,
        ])

        states = BoidSimulation(
            state=initial_state,
            seperation=0.3,
            cohesion=0.6,
            alignment=0.01,
            visibility=3,
        )

        figure["frames"] = [
            {
                "name":n,
                "data":[{
                    "x":state["px"],
                    "y":state["py"],
                    "mode":"markers",
                    "marker_symbol":np.where(
                        state["vx"].abs().lt(1) & state["vy"].abs().lt(1),
                        "circle",
                        "x",
                    ),
                }],
            }
            for n, state in enumerate(states)
        ]
        figure["data"] = figure["frames"][0]["data"]

        button = figure["layout"]["updatemenus"][0]["buttons"][0]
        slider = figure["layout"]["sliders"][0]
        
        button["args"][-1]["frame"]["duration"] = duration
        slider["transition"]["duration"] = duration
        slider["step"] = [
            {
                "label": frame["name"],
                "method": "animate",
                "args": [
                    [frame["name"]],
                    {"frame": {"duration": duration, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": duration}}
                ],
                }
            for frame in figure["frames"]
        ]
    
        return figure