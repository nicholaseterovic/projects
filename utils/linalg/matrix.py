import typing as tp
import itertools as it

from .container import Container, Numeric, numeric_types

###################################################################################################

class Matrix(Container):
    def __init__(self, data:object, n:int=None, m:int=None):
        self.data = self._get_data(data=data, n=n, m=m)
        self._validate()
    
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
    def T(self) -> object:
        keys = ((j, i) for i, j in self.data.keys())
        values = self.data.values()
        data = dict(zip(keys, values))
        return Matrix(data)

    def _get_data(self, data:object, n:int, m:int) -> tp.Dict[tp.Tuple[int, int], Numeric]:
        if data is not None:
            if isinstance(data, dict):
                return data
            if isinstance(data, tp.Iterable):
                if all(isinstance(row, tp.Iterable) for row in data):
                    return {
                        (i, j):datum
                        for i, row in self.enumerate(data)
                        for j, datum in self.enumerate(row)
                    }
        if n is not None:
            if m is None:
                m = n
            keys = list(it.product(self.range(n), self.range(m)))
            vals = it.starmap(self._get_datum, keys)
            data = dict(zip(keys, vals))
            return data
        raise ValueError

    def _validate(self) -> None:
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
    
    def __str__(self) -> str:
        matrix_str = ""
        I = list(self.I)
        J = list(self.J)
        for i in I:
            row_values = (self.data[(i, j)] for j in J)
            row_str = " ".join(map(self.value_frmt.format, row_values))
            matrix_str += row_str + "\n"
        return matrix_str

class IdentityMatrix(Matrix):
    def __init__(self, n:int, m:int=None):
        return super().__init__(data=None, n=n, m=m)
    
    def _get_datum(self, i:int, j:int) -> Numeric:
        return int(i==j)

class RowAdderMatrix(Matrix):
    def __init__(self, constant:Numeric, i:int, j:int, n:int, m:int=None):
        self._constant = constant
        self._i = i
        self._j = j
        super().__init__(data=None, n=n, m=m)
    
    def _get_datum(self, i:int, j:int) -> Numeric:
        return self._constant if (i, j)==(self._i, self._j) else int(i==j)