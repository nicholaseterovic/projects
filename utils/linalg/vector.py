import typing as tp
import itertools as it

from .container import Container, Numeric, numeric_types

class Vector(Container):
    def __init__(self, data:object, n:int=None):
        self.data = self._get_data(data=data, n=n)
        self._validate()
    
    @property
    def n(self) -> int:
        return len(self.data)
    
    @property
    def I(self) -> tp.Iterator[int]:
        return self.range(self.n)
    
    def _get_data(self, data:object, n:int) -> tp.Dict[int, Numeric]:
        if data is not None:
            if isinstance(data, dict):
                return data
            if isinstance(data, tp.Iterable):
                return {i:datum for i, datum in self.enumerate(data)}
        if n is not None:
            if isinstance(n, int):
                return {i:self._get_datum(i) for i in self.range(n)}
        raise ValueError
    
    def _validate(self) -> None:
        if not isinstance(self.data, dict):
            raise ValueError(f"Data {type(self.data)} is not a dict")
        if not self.data:
            raise ValueError(f"Data cannot be empty")
        if sorted(self.data.keys()) != sorted(self.I):
            raise ValueError(f"Data keys are not {self.I}")
        for datum in self.data.values():
            if not isinstance(datum, numeric_types):
                raise ValueError(f"Data {type(datum)} is not {numeric_types}")

    def __str__(self) -> str:
        return "\n".join(map(self.value_frmt.format, self.data))

class ConstantVector(Vector):
    def __init__(self, constant:Numeric, n:int):
        self._constant = constant
        super().__init__(data=None, n=n)

    def _get_datum(self, i:int) -> Numeric:
        return self._constant

class ZeroVector(ConstantVector):
    def __init__(self, n:int):
        return super().__init__(constant=0, n=n)

class UnitVector(ConstantVector):
    def __init__(self, n:int):
        return super().__init__(constant=1, n=n)