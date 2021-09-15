# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import abc
import math
import inspect
import typing as tp
import functools as ft
import itertools as it

# In-house packages.
import constants

# Dash packages.
import dash
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

####################################################################################################

class Shape(abc.ABC):

    axes = ['x', 'y', 'z']

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
        nonself_args = [arg for arg in args if arg!='self']
        dimension = len(nonself_args)
        return dimension

class Point(Shape):
    def __init__(self:object, *coordinates:tp.Tuple[float, ...]) -> object:
        self.coordinates = coordinates
    
    @classmethod
    def origin(cls:object) -> object:
        point = cls()
        return point

    def __iter__(self:object) -> iter:
        return iter(self.coordinates)
    
    def __repr__(self:object) -> str:
        return 'Point('+','.join(map(str, self))+')'
    
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

class Line(Shape):
    def __init__(self:object, p:Point, q:Point) -> object:
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
        return f'Line({self.p},{self.q})'
    
    def get_point(self:object, d:float=0) -> Point:
        pairs = it.zip_longest(self.p, self.q, fillvalue=0)
        coordinates = ((1-d)*pi+d*qi for pi, qi in pairs)
        point = Point(*coordinates)
        return point
    
    @property
    def length(self:object) -> float:
        return self.p.get_distance_to(self.q)

    def get_trace(self:object) -> dict:
        p_trace = self.p.get_trace()
        q_trace = self.q.get_trace()
        trace = {axis:p_trace[axis]+q_trace[axis] for axis in Shape.axes}
        return trace

class Polygon(Shape):
    def __init__(self:object, points:tp.Container[Point]) -> object:
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
    def __init__(self:object, line:Line, n:int=3) -> object:
        self.points = points

    @classmethod
    def unit(cls:object, n:int=3) -> object:
        line = Line.unit()
        unit = cls(line, n)
        return line

class Triangle(Polygon):
    def __init__(self:object, points:tp.Container[Point]) -> object:
        if len(points)!=3:
            raise ValueError(points)
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
    
class Ellipse(Shape):
    def __init__(self:object, line:Line, diameter:float) -> object:
        self.line = line
        self.diameter = diameter

    def __repr__(self:object) -> str:
        return f'Ellipse({self.line},{self.diameter})'

class Circle(Ellipse):
    def __init__(self:object, center:Point, radius:float) -> object:
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
        return f'Circle({self.center},{self.radius})'

class Spiral(Shape):
    def __init__(self:object, center:Point, radius:float) -> object:
        self.center = center
        self.radius = radius

    @classmethod
    def unit(cls:object) -> object:
        return cls(center=Point.origin(), radius=1)

    def get_point(self:object, radians:float=0) -> Point:
        sin = math.sin(radians)
        cos = math.cos(radians)
        point = self.center+Point(cos, sin)*(self.radius*radians*0.5/math.pi)
        return point
        
####################################################################################################
# LAYOUT

app_layout = [
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.InputGroupAddon(
                        children='Number of Seeds:',
                    ),
                    dbc.Input(
                        f'input-spiral-seeds',
                        value=100,
                        disabled=False,
                    ),
                    dbc.DropdownMenu(
                        id=f'dropdownmenu-spiral-turns',
                        label='Turns',
                        color='primary',
                        direction='right',
                        addon_type='prepend',
                        children=[]
                    ),
                    dbc.Input(
                        f'input-spiral-turns',
                        value=1,
                        disabled=False,
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children=[
                            dbc.Button(
                                id=f'button-fractal-{path}-undo',
                                children='Undo',
                                color='primary',
                                n_clicks=0,
                            ),
                        ],
                    ),
                    dbc.InputGroupAddon(
                        children='Modifying:',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children=[
                            dbc.Button(
                                id=f'button-fractal-{path}-mod',
                                children=fractal_segment_datum['name'],
                                color='primary',
                                n_clicks=1,
                            ),
                        ],
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dcc.Graph(
                id=f'graph-fractal-{path}',
                config={'displayModeBar':False, 'displaylogo':False},
                figure={
                    'layout':{
                        **empty_path_figure['layout'],
                        'dragmode':'drawline',
                        'title':f'{path.capitalize()} Construction',
                    },
                    'data':[
                        *empty_path_figure['data'],
                        *([interpolate_segment_datum] if path=='generator' else []),
                    ],
                },
            ),
        ])
    ])
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:
    return