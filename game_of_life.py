# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import typing as tp
import itertools as it

# In-house imports.
import constants

####################################################################################################

class GameOfLife(object):

    # Class attributes.
    _neighborhood:tp.List[tp.Tuple[int, int]] = list(it.product([-1, 0, +1], repeat=2))
    _min_neighbors:int = 2 # Minimum # neighhors required for a live cell to live on.
    _max_neighbors:int = 3 # Maximum # neighhors allowed for a live cell to live on.
    _pop_neighbors:int = 3 # Required # neighhors required for a dead cell to populate.

    def __init__(self, state:tp.List[tp.Tuple[int, int]]=[], stop:int=100) -> object:
        """
        > Initialize an iterator that yields state evolutions from John Conway's game of life. 
        
        Arguments:
            state: List-of-pairs [(x, y), ...], coordinates of initial live cells.
            stop: Maximum number of allowed state evolutions.

        Returns:
            Iterable yielding state evolutions.
        """
        # Check types.
        if not isinstance(stop, int) or stop<0:
            raise ValueError(f"Max step must be a positive integer: {stop}")
        if not isinstance(state, list):
            raise ValueError(f"State must be list: {state}")
        for xy in state:
            if not isinstance(xy, tuple):
                raise ValueError(f"State elements must be integer 2-tuples {state}")
            if len(xy) != 2:
                raise ValueError(f"State elements must be integer 2-tuples {state}")
            x, y = xy
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError(f"State elements must be integer 2-tuples {state}")
        # Set attributes.
        self.state = state
        self.stop = stop
        self._i = 0

    def __iter__(self) -> object:
        return self
    
    def __next__(self) -> tp.List[tp.Tuple[int, int]]:
        """
        > Return the next state evolution.
        
        Arguments:
            None

        Returns:
            List-of-pairs [(x, y), ...] coordinates of next live cells. 
        """
        if self._i>=self.stop:
            raise StopIteration
        state = GameOfLife._get_next_state(state=self.state)
        self.state = state
        self._i += 1
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
        """
        > Determines if a cell becomes alive.
        
        Arguments:
            num_neighbors: Number of neighboring live cells.
            is_alive: Indicates if cell is currently alive.

        Returns:
            Indicator if cell becomes alive.
        """
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

# Dash imports.
import dash
from dash import dcc
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_bootstrap_components as dbc

# Default widget parameters. 
default_rows = 25
default_cols = 25
default_tdur = 500

# Heatmap visualizing the game of life.
pause_info = "Click to Flip Cell State"
pause_title = "<br>".join([
    "<i>In Pause Mode</i>",
    "<b>Click Play</b> to Run Simulation or <b>Click or Box-Select Cells</b> to Flip State",
])
play_title = "<br>".join([
    "<i>In Play Mode</i>",
    "<b>Click Pause</b> to Stop Simulation and Edit Cells",
])
default_figure = {
    "layout":{
        "title":pause_title,
        "margin":{"l":0, "r":0, "b":0},
        "clickmode":"event+select",
        "dragmode":"select",
        "hovermode":"closest",
        "hoverdistance":1000,
        "xaxis":{"visible":False, "autorange":True},
        "yaxis":{"visible":False, "autorange":True, "scaleanchor":"x"},
    },
    "data":[{
        "type":"heatmap",
        "name":pause_info,
        "hoverinfo":"name",
        "hoverlabel":{"namelength":-1},
        "xgap":2,
        "ygap":2,
        "zmin":0,
        "zmax":1,
        "connectgaps":False,
        "showscale":False,
        "autocolorscale":False,
        "colorscale":[[0, "whitesmoke"], [1, constants.NAVBAR_COLOR]],
        **dict(zip(
            ["x", "y", "z"],
            zip(*it.product(range(default_cols), range(default_rows), [0])),
        )),
    }],
}

app_layout = [
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown(f"""
                # The Game of Life
                ***

                ### Introduction
                ***

                  This project is an implementation of 
                  [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life),
                  a population simulation governed by a small set of rules:

                1. *Any live cell with {GameOfLife._min_neighbors} or {GameOfLife._max_neighbors} live neighbours survives.*
                2. *Any dead cell with {GameOfLife._pop_neighbors} live neighbours becomes a live cell.*
                2. *All other live cells die in the next generation. Similarly, all other dead cells stay dead.*

                The neighborhood of a cell comprises the eight adjacent cells.
            """),
        ]),
    ]),
    dcc.Interval(
        id="interval-gol",
        interval=100,
        disabled=True,
    ),
    dcc.Store(
        id="store-gol",
        data={},
    ),
    dbc.Card([
        dbc.CardHeader([
            dcc.Markdown("""
                ### The Simulation
                ***
            """),
            dbc.InputGroup(
                size="sm",
                children=[
                    dbc.Button(
                        id="button-gol-clear",
                        children="Clear Cells",
                        n_clicks=0,
                        color="primary",
                        disabled=False,
                    ),
                    dbc.InputGroupText("Rows:"),
                    dbc.Select(
                        id="select-gol-rows",
                        value=default_rows,
                        options = [
                            {"value":dim, "label":dim}
                            for dim in [10, 25, 50, 75, 100]
                        ]
                    ),
                    dbc.InputGroupText("Cols:"),
                    dbc.Select(
                        id="select-gol-cols",
                        value=default_cols,
                        options = [
                            {"value":dim, "label":dim}
                            for dim in [10, 25, 50, 75, 100]
                        ]
                    ),
                    dbc.InputGroupText("Duration:"),
                    dbc.Select(
                        id="select-gol-tdur",
                        value=default_tdur,
                        options = [
                            {"value":dur, "label":f"{dur/1000:.1f}S"}
                            for dur in [100, 300, 500, 1000]
                        ]
                    ),
                    dbc.Button(
                        id="button-gol-state",
                        children="Play",
                        n_clicks=0,
                        color="primary",
                        disabled=False,
                    ),
                    dbc.Button(
                        id="icon-gol-state",
                        className="fa fa-play",
                        n_clicks=0,
                        color="primary",
                        disabled=False,
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dcc.Graph(
                id="graph-gol",
                style={"height":"50vw"},
                config={"displayModeBar":False, "displaylogo":False},
                figure=default_figure,
            ),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        [
            ddp.Output("button-gol-state", "children"),
            ddp.Output("button-gol-state", "color"),
            ddp.Output("button-gol-state", "disabled"),
            ddp.Output("icon-gol-state", "className"),
            ddp.Output("icon-gol-state", "children"),
            ddp.Output("icon-gol-state", "color"),
            ddp.Output("interval-gol", "disabled"),
        ],
        [
            ddp.Input("select-gol-cols", "value"),
            ddp.Input("select-gol-rows", "value"),
            ddp.Input("select-gol-tdur", "value"),
            ddp.Input("button-gol-state", "n_clicks"),
            ddp.Input("icon-gol-state", "n_clicks"),
            ddp.Input("tabs-projects", "value"),
        ],
        [
            ddp.State("button-gol-state", "children"),
            ddp.State("button-gol-state", "color"),
            ddp.State("button-gol-state", "disabled"),
            ddp.State("icon-gol-state", "className"),
            ddp.State("icon-gol-state", "children"),
            ddp.State("icon-gol-state", "color"),
            ddp.State("interval-gol", "disabled"),
        ],
    )
    def set_state(*args:tp.Tuple[int]) -> tuple:
        values, args  = args[:3], args[3:]
        if not all(values):
            return "Check Parameters", "primary", True, "fa fa-times", None, "primary", True
        _, _, tab, *states = args
        trigger = dash.callback_context.triggered[0]
        if trigger["prop_id"].startswith("select"):
            return states
        if trigger["prop_id"].endswith("n_clicks") and states[0]=="Play" and tab=="gol":
            return "Pause", "warning", False, None, dbc.Spinner(size="sm"), "warning", False
        return "Play", "primary", False, "fa fa-play", None, "primary", True
        
    @app.callback(
        [
            ddp.Output("graph-gol", "figure"),
            ddp.Output("graph-gol", "config"),
        ],
        [
            ddp.Input("button-gol-clear", "n_clicks"),
            ddp.Input("interval-gol", "n_intervals"),
            ddp.Input("interval-gol", "disabled"),
            ddp.Input("graph-gol", "clickData"),
            ddp.Input("graph-gol", "selectedData"),
        ],
        [
            ddp.State("select-gol-cols", "value"),
            ddp.State("select-gol-rows", "value"),
            ddp.State("select-gol-tdur", "value"),
            ddp.State("button-gol-state", "children"),
            ddp.State("graph-gol", "figure"),
            ddp.State("graph-gol", "config"),
            ddp.State("graph-gol", "loading_state"),
        ],
    )
    def plot_gol(
        n_clicks:int,
        n_intervals:int,
        disabled:bool,
        clickData:dict,
        selectedData:dict,
        cols:int,
        rows:int,
        tdur:int,
        state:str,
        figure:dict,
        config:dict,
        loading_state:bool,
    ) -> tp.Tuple[dict, dict]:
        trigger = dash.callback_context.triggered[0]
        if trigger["prop_id"].endswith("n_intervals"):
            # Throttle interval updates.
            tdur = int(tdur)
            n_intervals = int(n_intervals)
            if (100*n_intervals)%tdur:
                raise dex.PreventUpdate

        # Extract state.
        cols = int(cols)
        rows = int(rows)
        datum = figure["data"][0]

        # Set annotations.
        if state=="Play":
            figure["layout"]["title"] = pause_title
            datum["name"] = pause_info
        elif state=="Pause":
            figure["layout"]["title"] = play_title
            datum["name"] = ""
        
        if trigger["prop_id"].endswith("clickData") or trigger["prop_id"].endswith("selectedData"):
            if state=="Pause" or trigger["value"] is None:
                raise dex.PreventUpdate
            # Flip selected cells.
            points = trigger["value"].get("points", [])
            if "range" in trigger["value"]:
                xmin, xmax = trigger["value"]["range"]["x"]
                ymin, ymax = trigger["value"]["range"]["y"]
                points.extend(
                    {"x":x, "y":y}
                    for x in range(int(xmin)+1, int(xmax))
                    if 0<=x<cols
                    for y in range(int(ymin)+1, int(ymax))
                    if 0<=y<rows
                )
            for point in points:
                i = rows*point["x"] + point["y"]
                datum["z"][i] = 1 - datum["z"][i]
            return figure, config
        
        if trigger["prop_id"].endswith("clear.n_clicks"):
            # Clear cells.
            cells = []
        else:
            # Extract live cells.
            cells = [(x, y) for x, y, z in zip(datum["x"], datum["y"], datum["z"]) if z]
            if trigger["prop_id"].endswith("n_intervals"):
                gol = GameOfLife(state=cells)
                cells = next(gol)
        
        xyzd = dict(zip(
            ["x", "y", "z"],
            zip(*[(*xy, int(xy in cells)) for xy in it.product(range(cols), range(rows))]),
        ))
        datum.update(xyzd)
        return figure, config
        
