# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source imports.
import abc
import math
import inspect
import numpy as np
import typing as tp
import functools as ft
import itertools as it

# In-house imports.
import constants
import utils.graphic as gu

####################################################################################################

class Shape(abc.ABC):

    axes = ["x", "y", "z"]

    def get_distance_to(self:object, other:object) -> float:
        raise NotImplementedError

    def get_point(self:object, *args:tp.Tuple[float, ...]) -> object:
        raise NotImplementedError
    
    def get_points(self:object, *args:tp.Tuple[float, ...]) -> list:
        return list(it.starmap(self.get_point, it.product(*args)))

    @property
    def dimension(self:object) -> int:
        argspec = inspect.getfullargspec(self.get_point)
        args = argspec.args
        nonself_args = [arg for arg in args if arg!="self"]
        dimension = len(nonself_args)
        return dimension

####################################################################################################
# ZERO DIMENSIONS

class Point(Shape):
    def __init__(self:object, *coordinates:tp.Tuple[float, ...]) -> object:
        if not all(isinstance(coord, (int, float)) for coord in coordinates):
            raise ValueError(f"Coordinates must be numeric")
        self.coordinates = coordinates
    
    @classmethod
    def origin(cls:object) -> object:
        point = cls()
        return point

    def __iter__(self:object) -> iter:
        return iter(self.coordinates)
    
    def __repr__(self:object) -> str:
        return "Point("+",".join(map(str, self))+")"
    
    def __mul__(self:object, other:Shape) -> Shape:
        if isinstance(other, (int, float)):
            coordinates = (pi*other for pi in self)
            return Point(*coordinates)
        raise NotImplementedError

    def __add__(self:object, other:Shape) -> Shape:
        if isinstance(other, Point):
            pairs = it.zip_longest(self, other, fillvalue=0)
            coordinates = (pi+qi for pi, qi in pairs)
            return Point(*coordinates)
        raise NotImplementedError
    
    def __sub__(self:object, other:Shape) -> Shape:
        if isinstance(other, Point):
            return self+other*-1
        raise NotImplementedError
            
    def get_point(self:object) -> Shape:
        return self
    
    def get_distance_to(self:object, other:Shape) -> float:
        if isinstance(other, Point):
            return sum(d**2 for d in self-other)**0.5
        raise NotImplemented

    def get_trace(self:object) -> dict:
        pairs = it.zip_longest(Shape.axes, self.coordinates[:3], fillvalue=0)
        trace = {axis:[coordinate] for axis, coordinate in pairs}
        return trace

####################################################################################################
# ONE DIMENSION

class Line(Shape):
    def __init__(self:object, p:Point, q:Point) -> object:
        if not isinstance(p, Point) or not isinstance(q, Point):
            raise ValueError(f"Start and end points are required.")
        self.p = p
        self.q = q

    def __iter__(self:object) -> iter:
        return iter((self.p, self.q))

    @classmethod
    def unit(cls:object) -> object:
        p = Point()
        q = Point(1)
        line = cls(p, q)
        return line

    def __repr__(self:object) -> str:
        return f"Line({self.p},{self.q})"
    
    def get_point(self:object, d:float=0) -> Point:
        pairs = it.zip_longest(self.p, self.q, fillvalue=0)
        coordinates = ((1-d)*pi+d*qi for pi, qi in pairs)
        point = Point(*coordinates)
        return point
    
    @property
    def length(self:object) -> float:
        return self.p.get_distance_to(self.q)

    def get_intersection(self:object, other:object) -> Shape:
        if isinstance(other, Point):
            L = list(other-self.p, other-self.q, fillvalue=0)
            return L
        raise NotImplementedError


    def get_trace(self:object) -> dict:
        p_trace = self.p.get_trace()
        q_trace = self.q.get_trace()
        trace = {axis:p_trace[axis]+q_trace[axis] for axis in Shape.axes}
        return trace

####################################################################################################
# TWO DIMENSIONS

class Polygon(Shape):
    def __init__(self:object, points:tp.Tuple[Point, ...]) -> object:
        if not all(isinstance(point, Point) for point in points):
            raise ValueError("Points are required")
        if len(points) < 3:
            raise ValueError("At least three points are required.")
        self.points = points

    @property
    def lines(self:object) -> tp.List[Line]:
        points = self.points
        lines = []
        lines.extend(Line(p, q) for p, q in zip(points[:-1], points[1:]))
        lines.extend(Line(p, q) for p, q in zip(points[-1:], points[:1]))
        return lines

    @property
    def perimeter(self:object) -> float:
        return sum(line.length for line in self.lines)

    def get_trace(self:object) -> dict:
        line_traces = [line.get_trace() for line in self.lines]
        trace = {
            axis:ft.reduce(lambda x,y:x+[None]+y, [trace[axis] for trace in line_traces])
            for axis in Shape.axes
        }
        return trace

class RegularPolygon(Polygon):
    def __init__(self:object, sides:int, center:Point=Point.origin()) -> object:
        if not isinstance(sides, int):
            raise ValueError("An integer number of sides are required.")
        if sides < 3:
            raise ValueError("At least three sides are required.")
        if not isinstance(center, Point):
            raise ValueError("The center must be a Point.")
        angles = np.linspace(start=0, stop=2*math.pi, num=sides, endpoint=False)
        points = [
            center+Point(math.cos(angle), math.sin(angle))
            for angle in angles
        ]
        return super().__init__(points=points)

class Triangle(Polygon):
    def __init__(self:object, points:tp.Tuple[Point, ...]) -> object:
        if len(points)!=3:
            raise ValueError("Three points are required.")
        self.points = points
    
    @classmethod
    def unit(cls:object) -> object:
        p = Point()
        q = Point(1)
        line = cls(p, q)
        return line

    @property
    def area(self:object) -> object:
        semiperimeter = self.perimeter/2
        lengths = (semiperimeter-line.length for line in self.lines)
        area = (semiperimeter*ft.reduce(float.__mul__, lengths))**0.5
        return area

class EquilateralTriangle(RegularPolygon, Triangle):
    def __init__(self:object, center:Point=Point.origin()) -> object:
        return super().__init__(sides=3, center=center)

class Quadrilateral(Polygon):
    def __init__(self:object, points:tp.Tuple[Point, ...]) -> object:
        if len(points)!=4:
            raise ValueError("Four points are required.")
        self.points = points
    
class Ellipse(Shape):
    def __init__(self:object, line:Line, diameter:float) -> object:
        if not isinstance(line, Line):
            raise ValueError("Line is required")
        if not isinstance(diameter, (int, float)):
            raise ValueError("Diameter must be numeric")
        self.line = line
        self.diameter = diameter

    def __repr__(self:object) -> str:
        return f"Ellipse({self.line},{self.diameter})"

class Circle(Ellipse):
    def __init__(self:object, center:Point, radius:float) -> object:
        if not isinstance(center, Point):
            raise ValueError("Center must be a Point")
        if not isinstance(radius, (int, float)):
            raise ValueError("Radius must be numeric")
        self.center = center
        self.radius = radius
        super.__init__(line=Line(center, center), diameter=2*radius)
    
    @classmethod
    def unit(cls:object) -> object:
        line = Line.unit()
        circle = cls.from_line(line)
        return circle

    @classmethod
    def from_line(cls:object, line:Line) -> object:
        p, q = line
        return Circle(center=p, radius=p.get_distance_to(q))

    def __repr__(self:object) -> str:
        return f"Circle({self.center},{self.radius})"

class Spiral(Shape):
    def __init__(self:object, center:Point, radius:float) -> object:
        if not isinstance(center, Point):
            raise ValueError("Center must be a Point.")
        if not isinstance(radius, (int, float)):
            raise ValueError("Radius must be numeric")
        self.center = center
        self.radius = radius

    @classmethod
    def unit(cls:object) -> object:
        return cls(center=Point.origin(), radius=1)

    def get_point(self:object, radians:float=0) -> Point:
        sin = math.sin(radians)
        cos = math.cos(radians)
        point = self.center+Point(cos, sin)*(self.radius*radians/math.pi/2)
        return point

####################################################################################################
# THREE DIMENSIONS

class Polyhedron(Shape):
    def __init__(self:object, polygons:tp.Tuple[Polygon, ...]) -> object:
        self.polygons = polygons

class RegularPolyhedron(Polyhedron):
    pass

class Tetrahedron(RegularPolygon):
    def __init__(self:object) -> object:
        polygons = []
        raise NotImplementedError
        super.__init__(polygons=polygons)

class Tetrahedron(RegularPolygon):
    def __init__(self:object) -> object:
        polygons = []
        raise NotImplementedError
        super.__init__(polygons=polygons)

class Tetrahedron(RegularPolygon):
    def __init__(self:object) -> object:
        polygons = []
        raise NotImplementedError
        super.__init__(polygons=polygons)

class Tetrahedron(RegularPolygon):
    def __init__(self:object) -> object:
        polygons = []
        raise NotImplementedError
        super.__init__(polygons=polygons)
        
####################################################################################################
# LAYOUT

# Dash imports.
import dash
from dash import dcc
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_bootstrap_components as dbc

app_layout = [
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown("""
                # Geometry
                ***

                ### Introduction
                ***

                  This page is a home to my *computational geometry* projects,
                modelling shapes and patterns of various kind and dimension.
            """),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dcc.Markdown("""
                ### Sunflower Seeds and the Golden Ratio
                ***

                  Perhaps one of the strongest examples of how mathematics underpins nature
                is the **golden ratio** $ \phi = (1+\sqrt{5})/2$. This constant can be found
                in many of nature'sdesigns. Here, an example is given by modelling
                an arrangement of **sunflower seeds** using a spiral; at every $\phi$ turns
                of the spiral a seed is grown.
                  
            """),
            dbc.InputGroup(
                size="sm",
                children=[
                    dbc.Button(
                        id="button-geometry-spiral-reset",
                        children="Reset",
                        n_clicks=0,
                        color="primary",
                    ),
                    dbc.InputGroupText(
                        children="Seed Count:",
                    ),
                    dbc.Input(
                        id="input-geometry-spiral-snum",
                        value=300,
                        type="numeric",
                        disabled=True,
                    ),
                    dbc.InputGroupText(
                        children="Rotation Space:",
                    ),
                    dbc.Input(
                        id="input-geometry-spiral-tmin",
                        value="(1+5**0.5)/2",
                    ),
                    dbc.Input(
                        id="input-geometry-spiral-tmax",
                        value="1",
                    ),
                    dbc.Input(
                        id="input-geometry-spiral-tnum",
                        value=50,
                        type="numeric",
                        disabled=True,
                    ),
                    dbc.InputGroupText(
                        children="Draw Lines:",
                    ),
                    dbc.InputGroupText(
                        children=[
                            dbc.Checkbox(
                                id="checkbox-geometry-spiral-mode",
                                value=True,
                            ),
                        ],
                    ),
                    dbc.Button(
                        id="button-geometry-spiral-plot",
                        children="Generate",
                        n_clicks=0,
                        color="primary",
                        disabled=False,
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dcc.Graph(
                id="graph-geometry-spiral",
                config={"displayModeBar":False, "displaylogo":False},
                figure={
                    "data":[],
                    "frames":[],
                    "layout":{
                        "hovermode":"closest",
                        "xaxis":{"visible":True, "range":[-1, 1], "autorange":False},
                        "yaxis":{"visible":True, "range":[-1, 1], "autorange":False, "scaleanchor":"x"},
                        "margin":{"t":0, "b":0, "l":0, "r":0, "pad":0},
                        "updatemenus":[
                            {
                                "type": "buttons",
                                "direction": "left",
                                "yanchor": "top",
                                "xanchor": "left",
                                "x": 0,
                                "y": 0,
                                "pad": {"r": 25, "t": 50},
                                "showactive": True,
                                "buttons": [
                                    {
                                        "label": "Play",
                                        "method": "animate",
                                        "args": [
                                            None,
                                            {
                                                "frame": {"duration": 1000, "redraw": False},
                                                "fromcurrent": True,
                                                "transition": {"duration": 0, "easing": "linear"},
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
                                "currentvalue": {
                                    "font": {"size": 20},
                                    "prefix": "Rotation:",
                                    "xanchor": "left",
                                    "visible": True,
                                },
                                "yanchor": "top",
                                "xanchor": "left",
                                "x": 0.1,
                                "y": 0,
                                "len": 0.9,
                                "transition": {"duration": 0, "easing": "linear"},
                                "pad": {"l":25, "b": 10, "t": 50},
                                "steps": [],
                            },
                        ],
                    },
                },
            ),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dcc.Markdown("""
                ### Polygons and their Properties
                ***

                  <Insert text here>
                  
            """),
            dbc.InputGroup(
                size="sm",
                children=[
                    dbc.Button(
                        id="button-geometry-polygon-clear",
                        children="Clear",
                        n_clicks=0,
                        color="warning",
                    ),
                    dbc.InputGroupText(
                        children="Polygon With Sides:",
                    ),
                    dbc.Input(
                        id="input-geometry-polygon-sides",
                        value=3,
                        type="numeric",
                        min=3,
                        max=100,
                        step=1,
                    ),
                    dbc.Button(
                        id="button-geometry-polygon-add",
                        children="Add",
                        n_clicks=0,
                        color="primary",
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dcc.Graph(
                id="graph-geometry-polygon",
                config={"displayModeBar":False, "displaylogo":False},
                figure={
                    "data":[],
                    "layout":{
                        "hovermode":"closest",
                        "xaxis":{"visible":True, "range":[-1, 1], "autorange":False},
                        "yaxis":{"visible":True, "range":[-1, 1], "autorange":False, "scaleanchor":"x"},
                        "margin":{"t":0, "b":0, "l":0, "r":0, "pad":0},
                    },
                },
            ),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        ddp.Output("button-geometry-spiral-plot", "n_clicks"),
        [ddp.Input("tabs-projects", "value")],
        [ddp.State("button-geometry-spiral-plot", "n_clicks")],
    )
    def click_plot(tab:str, n_clicks:int) -> int:
        if tab!="geometry" or n_clicks>0:
            raise dex.PreventUpdate
        return n_clicks+1

    @app.callback(
        [
            ddp.Output("input-geometry-spiral-snum", "value"),
            ddp.Output("input-geometry-spiral-tmin", "value"),
            ddp.Output("input-geometry-spiral-tmax", "value"),
            ddp.Output("input-geometry-spiral-tnum", "value"),
            ddp.Output("checkbox-geometry-spiral-mode", "value"),
        ],
        [ddp.Input("button-geometry-spiral-reset", "n_clicks"),],
    )
    def click_reset(n_clicks:int) -> int:
        return (
            300,
            "(1+5**0.5)/2",
            "1",
            50,
            True,
        )
        
    @app.callback(
        ddp.Output("graph-geometry-spiral", "figure"),
        [ddp.Input("button-geometry-spiral-plot", "n_clicks")],
        [
            ddp.State("graph-geometry-spiral", "figure"),
            ddp.State("input-geometry-spiral-snum", "value"),
            ddp.State("input-geometry-spiral-tmin", "value"),
            ddp.State("input-geometry-spiral-tmax", "value"),
            ddp.State("input-geometry-spiral-tnum", "value"),
            ddp.State("checkbox-geometry-spiral-mode", "value"),
        ],
    )
    def plot_spiral(n_clicks:int, figure:dict, snum:int, tmin:float, tmax:float, tnum:int, lines:bool) -> dict:
        tmin = eval(tmin, {}, {})
        tmax = eval(tmax, {}, {})
        tnum = int(tnum)
        snum = int(snum)
        mode = "markers+lines" if lines else "markers"
        rgb = gu.hex_to_rgb(constants.NAVBAR_COLOR)
        figure["frames"] = []
        for t in np.linspace(start=tmin, stop=tmax, num=tnum):
            mesh = t*2*math.pi*np.linspace(start=1, stop=snum, num=snum)
            spiral = Spiral(center=Point.origin(), radius=1/snum/t)
            points = spiral.get_points(mesh)
            sizes = [5+int(10*i/snum) for i, _ in enumerate(points, 1)]
            x, y = zip(*points)
            frame = {
                "name":f"{t:0.3f}",
                "data":[{
                    "x":x,
                    "y":y,
                    "mode":mode,
                    "marker":{"color":"rgba({},{},{},1)".format(*rgb), "size":sizes},
                    "line":{"color":"rgba({},{},{},0.2)".format(*rgb)},
                }],
            }
            figure["frames"].append(frame)
        figure["data"] = figure["frames"][0]["data"]
        figure["layout"]["sliders"][0]["steps"] = [
            {
                "method":"animate",
                "label":frame["name"],
                "args": [
                    [frame["name"]],
                    {
                        "mode":"immediate",
                        "transition":{"duration":0},
                        "frame":{"duration":0, "redraw":False},
                    }
                ],
                }
            for frame in figure["frames"]
        ]
        return figure

    @app.callback(
        ddp.Output("graph-geometry-polygon", "figure"),
        [
            ddp.Input("button-geometry-polygon-clear", "n_clicks"),
            ddp.Input("button-geometry-polygon-add", "n_clicks"),
        ],
        [
            ddp.State("input-geometry-polygon-sides", "value"),
            ddp.State("graph-geometry-polygon", "figure"),
        ],
    )
    def add_polygon(clear_clicks:int, add_clicks:int, sides:int, figure:dict) -> dict:
        trigger = dash.callback_context.triggered[0]
        if trigger['prop_id'].endswith('clear.n_clicks'):
            figure['data'].clear()
            return figure
        sides = int(sides)
        polygon = RegularPolygon(sides=sides)
        trace = polygon.get_trace()
        figure['data'].append(trace)
        return figure