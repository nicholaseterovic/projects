import abc
import inspect
import typing as tp
import functools as ft
import itertools as it

class Shape(abc.ABC):

    @property
    def dimension(self:object) -> int:
        argspec = inspect.getfullargspec(self.get_point)
        args = argspec.args
        nonself_args = [arg for arg in args if arg!='self']
        dimension = len(nonself_args)
        return dimension

    def get_point(self:object, *args:tp.Tuple[float, ...]) -> object:
        raise NotImplementedError
    
    def get_distance_to(self:object, other:object) -> float:
        raise NotImplementedError

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

class Triangle(Polygon):
    def __init__(self:object, points:tp.Container[Point]) -> object:
        if len(points)!=3:
            raise ValueError(points)
        self.points = points
    
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
    def from_line(cls:object, line:Line) -> object:
        p, q = line
        return Circle(center=p, radius=p.get_distance_to(q))

    def __repr__(self:object) -> str:
        return f'Circle({self.center},{self.radius})'

    @classmethod
    def unit(cls:object) -> object:
        line = Line.unit()
        circle = cls.from_line(line)
        return circle