

import typing as tp
import itertools as it

numeric_types = (int, float, complex)

class Container(object):
    value_frmt = "{:}"

class Vector(Container):

    @classmethod
    def zero(cls, n:int) -> object:
        data = (0 for _ in range(n))
        return cls(data=data, validate=False)

    def __init__(self, data:tp.Iterator, validate:bool=True) -> int:
        data = tuple(data)
        if validate:
            self._validate_data(data=data)
        self._data = tuple(data)

    def __str__(self) -> str:
        return "\n".join(map(self.value_frmt.format, self._data))

    @property
    def n(self) -> int:
        return len(self._data)
    
    @staticmethod
    def _validate_data(data:tuple) -> None:
        if not isinstance(data, tuple):
            raise ValueError("Vector data must be a tuple")
        for val in data:
            if not isinstance(val, numeric_types):
                raise ValueError("Vector data must be numeric")

class Matrix(Container):
    
    @classmethod
    def identity(cls, n:int, m:int=None) -> object:
        if m is None:
            m = n
        data = {(i, j):int(i==j) for i in range(1, n+1) for j in range(1, m+1)}
        return cls(data=data)
    
    def __init__(self, data:tp.Dict, validate:bool=True) -> object:
        if validate:
            self._validate_data(data=data)
        self._data = data

    def __str__(self) -> str:
        matrix_str = ""
        I = list(self.I)
        J = list(self.J)
        for i in I:
            row_values = (self._data[(i, j)] for j in J)
            row_str = " ".join(map(self.value_frmt.format, row_values))
            matrix_str += row_str + "\n"
        return matrix_str
    
    @property
    def n(self) -> int:
        return self.shape[0]

    @property
    def m(self) -> int:
        return self.shape[1]

    @property
    def shape(self) -> tp.Tuple[int, int]:
        return tuple(map(len, map(set, zip(*self._data.keys()))))
    
    @property
    def I(self) -> tp.Iterator[int]:
        return range(1, self.n+1)

    @property
    def J(self) -> tp.Iterator[int]:
        return range(1, self.m+1)
    
    @property
    def T(self) -> object:
        keys = ((j, i) for i, j in self._data.keys())
        values = self._data.values()
        data = dict(zip(keys, values))
        return Matrix(data=data, validate=False)
    
    @staticmethod
    def _validate_data(data) -> None:
        if not isinstance(data, dict):
            raise ValueError("Matrix data must be dict")
        for key, val in data.items():
            if not isinstance(key, tuple) or len(key) != 2:
                raise ValueError(f"Matrix key not a two-tuple: {key}")
            i, j = key
            if not isinstance(i, int) or not isinstance(j, int):
                raise ValueError(f"Matrix key not an integer pair {key}")
            if not isinstance(val, (int, float, complex)):
                raise ValueError(f"Matrix value must be numeric")
        n, m = map(len, map(set, zip(*data.keys())))
        if sorted(data.keys()) != sorted(it.product(range(1, n+1), range(1, m+1))):
            raise ValueError("Matrix keys do not form rectangle")