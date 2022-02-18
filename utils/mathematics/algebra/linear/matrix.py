# Nicholas Eterovic 2022Q1
####################################################################################################

# Open-source imports.
from multiprocessing.sharedctypes import Value
import typing as tp
import itertools as it
 
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
        I = list(self.I)
        J = list(self.J)
        return (Vector(data=(self.data[(i, j)] for j in J)) for i in I)

    @property
    def cols(self) -> tp.Iterable[Vector]:
        I = list(self.I)
        J = list(self.J)
        return (Vector(data=(self.data[(i, j)] for i in I)) for j in J)
    
    @property
    def T(self) -> object:
        keys = ((j, i) for i, j in self.data.keys())
        vals = self.data.values()
        data = dict(zip(keys, vals))
        return self.__class__(data=data, validate=False)

    def is_symmetric(self) -> bool:
        return self == self.T
    
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
    
    def __getitem__(self, arg:tp.Tuple[tp.Union[int, slice]]) -> object:
        i, j = arg
        I = self.I[self.slice(i)]
        J = self.J[self.slice(j)]
        if isinstance(I, int):
            if isinstance(J, int):
                return self.data[(i, j)]
            data = {j:self.data[(i, j)] for j in J}
            return Vector(data=data, validate=False)
        if isinstance(J, int):
            data = {i:self.data[(i, j)] for i in I}
            return Vector(data=data, validate=False)
        data = {(i, j):self.data[(i, j)] for i in I for j in J}
        return Matrix(data=data, validate=False)
            
    def __str__(self) -> str:
        matrix_str = ""
        I = list(self.I)
        J = list(self.J)
        for i in I:
            row_values = (self.data[(i, j)] for j in J)
            row_str = " ".join(map(self._value_frmt.format, row_values))
            matrix_str += row_str + "\n"
        return matrix_str

    def __mul__(self, other) -> object:
        if isinstance(other, Vector):
            return Vector(data=(row*other for row in self.rows))
        raise NotImplementedError(type(other))

    @classmethod
    def variable(cls, name:str, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            data[(i, j)] = Variable(name=f"{name}_{i}_{j}")
        return cls(data=data, validate=False)

    @classmethod
    def identity(cls, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            data[(i, j)] = int(i==j)
        return cls(data=data, validate=False)

    @classmethod
    def row_permuter(cls, ri:int, rj:int, n:int, m:int=None):
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

    @classmethod
    def row_adder(cls, ri:int, rj:int, constant:Numeric, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(cls.range(n), cls.range(m)):
            if (i, j) == (ri, rj):
                data[(i, j)] = constant
            else:
                data[(i, j)] = int(i==j)
        return cls(data=data, validate=False)

def get_row_echelon(matrix:Matrix) -> tp.Tuple[Matrix, tp.Iterable[Matrix]]:
    h = 1
    k = 1
    n = matrix.n
    m = matrix.m
    cols = matrix.cols
    while h <= n and k <= m:
        col = next(cols)
        pivot = col.pivot
        