# Nicholas Eterovic 2022Q1
####################################################################################################

# Open-source imports.
import math
import typing as tp
import itertools as it
import functools as ft

# In-house imports.
from .vector import Vector
from ..expression import Variable
from .container import Container, Numeric, numeric_types

##################################################################################################

class Matrix(Container):
    def __init__(self, data:object, validate:bool=True):
        self.data = self._normalize_data(data=data)
        if validate:
            self._validate_data()
    
    @property
    def n(self) -> int:
        return len(set(i for i, j in self.data.keys()))

    @property
    def I(self) -> tp.Iterator[int]:
        return self.range(self.n)

    @property
    def m(self) -> int:
        return len(set(j for i, j in self.data.keys()))

    @property
    def J(self) -> tp.Iterator[int]:
        return self.range(self.m)
    
    @property
    def rows(self) -> tp.Iterable[Vector]:
        J = list(self.J)
        return (Vector(data=[self.data[(i, j)] for j in J]) for i in self.I)

    @property
    def cols(self) -> tp.Iterable[Vector]:
        I = list(self.I)
        return (Vector(data=[self.data[(i, j)] for i in I]) for j in self.J)
    
    @property
    def T(self) -> object:
        keys = ((j, i) for i, j in self.data.keys())
        vals = self.data.values()
        data = dict(zip(keys, vals))
        return self.__class__(data=data, validate=False)

    @property
    def is_square(self) -> bool:
        return self.n == self.m
    
    @property
    def is_symmetric(self) -> bool:
        return self == self.T

    @property
    def LU(self) -> tp.Tuple[object, object]:
        U, ops = get_row_echelon_form(M=self)
        L = ft.reduce(Matrix.dot, reversed(op.inv() for op in ops))
        return L, U

##################################################################################################

    def dot(self, other) -> object:
        if isinstance(other, numeric_types):
            data = {key:other*val for key, val in self.data.items()}
            return Matrix(data=data, validate=False)
        if isinstance(other, Vector):
            if self.m != other.n:
                raise ValueError(f"Incompatible dimensions {self.m} and {other.n}")
            data = [row*other for row in self.rows]
            return Vector(data=data, validate=False)
        if isinstance(other, Matrix):
            if self.m != other.n:
                raise ValueError(f"Incompatible dimensions {self.m} and {other.n}")
            data = [[row*col for col in other.cols] for row in self.rows]
            return Matrix(data=data, validate=False)
        raise NotImplementedError(type(other))

    def inv(self) -> object:
        if self.is_identity:
            return self
        if self.is_row_permuter:
            return self.T            
        raise NotImplementedError

##################################################################################################

    @staticmethod
    def _normalize_data(data:object) -> tp.Dict[tp.Tuple[int, int], Numeric]:
        if isinstance(data, dict):
            return data
        if isinstance(data, tp.Iterable):
            if all(isinstance(row, tp.Iterable) for row in data):
                return {
                    (i, j):datum
                    for i, row in Container.enumerate(data)
                    for j, datum in Container.enumerate(row)
                }
        raise NotImplementedError(type(data))

    def _validate_data(self) -> None:
        if not isinstance(self.data, dict):
            raise ValueError
        for key, val in self.data.items():
            if not isinstance(key, tuple) or len(key) != 2:
                raise ValueError
            i, j = key
            if not isinstance(i, int) or not isinstance(j, int):
                raise ValueError
            if not isinstance(val, numeric_types):
                raise ValueError
        if sorted(self.data.keys()) != sorted(it.product(self.I, self.J)):
            raise ValueError
    
    def __mul__(self, other) -> object:
        return self.dot(other=other)
    
    def __getitem__(self, arg:tp.Tuple[tp.Union[int, slice]]) -> object:
        i, j = arg
        I = self.I[self.slice(i)]
        J = self.J[self.slice(j)]
        if isinstance(I, int):
            if isinstance(J, int):
                return self.data[(i, j)]
            elif isinstance(J, (range, slice)):
                data = {l:self.data[(i, j)] for l, j in self.enumerate(J)}
                return Vector(data=data, validate=False)
        elif isinstance(I, (range, slice)):
            if isinstance(J, int):
                data = {k:self.data[(i, j)] for k, i in self.enumerate(I)}
                return Vector(data=data, validate=False)
            elif isinstance(J, (range, slice)):
                data = {(k, l):self.data[(i, j)] for k, i in self.enumerate(I) for l, j in self.enumerate(J)}
                return Matrix(data=data, validate=False)
        raise ValueError(type(I), type(J))
            
    def __str__(self) -> str:
        matrix_str = ""
        I = list(self.I)
        J = list(self.J)
        for i in I:
            row_values = (self.data[(i, j)] for j in J)
            row_str = " ".join(map(self._value_frmt.format, row_values))
            matrix_str += row_str + "\n"
        return matrix_str
        
##################################################################################################

    @classmethod
    def Variable(cls, name:str, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            data[(i, j)] = Variable(name=f"{name}_{i}_{j}")
        return cls(data=data, validate=False)

    @classmethod
    def Identity(cls, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            data[(i, j)] = int(i==j)
        return cls(data=data, validate=False)
    
    @property
    def is_identity(self) -> bool:
        for (i, j), val in self.data.items():
            if i == j:
                if val != 1:
                    return False
            else:
                if val != 0:
                    return False
        return True

    @classmethod
    def RowPermuter(cls, ri:int, rj:int, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            if i == ri:
                data[(i, j)] = int(j==rj)
            elif i == rj:
                data[(i, j)] = int(j==ri)
            else:
                data[(i, j)] = int(i==j)
        return cls(data=data, validate=False)
    
    @property
    def is_row_permuter(self) -> bool:
        raise NotImplementedError
    
    @classmethod
    def RowAdder(cls, ri:int, rj:int, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            if (i, j) == (ri, rj):
                data[(i, j)] = 1
            else:
                data[(i, j)] = int(i==j)
        return cls(data=data, validate=False)

    @property
    def is_row_adder(self) -> bool:
        raise NotImplementedError
    
    @classmethod
    def RowMultiplier(cls, ri:int, constant:Numeric, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            if (i, j) == (ri, ri):
                data[(i, j)] = constant
            else:
                data[(i, j)] = int(i==j)
        return cls(data=data, validate=False)

    @property
    def is_row_multiplier(self) -> tp.Tuple[int, Numeric]:
        raise NotImplementedError
    
    @classmethod
    def Rotator(cls, radians:float, n:int):
        if n == 2:
            cos = math.cos(radians)
            sin = math.sin(radians)
            data = [
                [+cos, -sin],
                [+sin, +cos],
            ]
            return cls(data=data, validate=False)
        raise NotImplementedError(n)

##################################################################################################

def get_row_echelon_form(M:Matrix) -> tp.Tuple[Matrix, tp.List[Matrix]]:
    """
    Returns:
        Matrix, input matrix transformed to row-echelon form.
        List of Matrix, sequence of applied elementary operations.
    """
    i = 1
    j = 1
    n = M.n
    m = M.m
    ops = []
    while i <= n and j <= m:
        vals = M[i:n, j]
        pivot = max(vals, key=abs, default=0)
        if pivot == 0:
            j += 1
            continue
        k = min(k for k, x in enumerate(vals, i) if x == pivot)
        if k != i:
            # Swap rows so that largest non-zero value is in pivot position.
            P = Matrix.RowPermuter(ri=i, rj=k, n=n)
            M = P * M
            ops.append(P)
        vals = M[i+1:n, j]
        for k, val in enumerate(vals, i+1):
            if val == 0:
                continue
            # Scale row so that first value is equal and opposite to pivot.
            c = - pivot / val
            C = Matrix.RowMultiplier(ri=k, constant=c, n=n)
            M = C * M
            # Add pivot row to cancel out first value.
            ops.append(C)
            A = Matrix.RowAdder(ri=k, rj=i, n=n)
            M = A * M
            ops.append(A)
        i += 1
        j += 1
    return M, ops