# Nicholas Eterovic 2022Q1
####################################################################################################

# Open-source imports.
import typing as tp
import itertools as it

# In-house imports.
from .container import *
from ..expression import *

####################################################################################################

class Vector(Container):

    @property
    def n(self) -> int:
        return len(self.data)
    
    @property
    def I(self) -> tp.Iterator[int]:
        return self.range(self.n)

    @property
    def pivot(self) -> tp.Union[None, Numeric]:
        for val in self:
            if val != 0:
                return val
        return None

##################################################################################################

    def dot(self, other:object) -> object:
        if isinstance(other, numeric_types):
            data = {key:other*val for key, val in self.data.items()}
            return Vector(data=data, validate=False)
        if isinstance(other, Vector):
            if self.n != other.n:
                raise ValueError(f"Incompatible dimensions {self.n} and {other.n}")
            return sum(self.data[i]*other.data[i] for i in self.I)
        raise NotImplementedError(type(other))

    def __mul__(self, other:object) -> object:
        return self.dot(other=other)
    
##################################################################################################

    @staticmethod
    def _normalize_data(data:object) -> tp.Dict[int, Numeric]:
        if isinstance(data, dict):
            return data
        if isinstance(data, tp.Iterable):
            return {i:datum for i, datum in Container.enumerate(data)}
        raise ValueError
    
    def _validate_data(self) -> None:
        if not isinstance(self.data, dict):
            raise ValueError(f"Data {type(self.data)} is not a dict")
        if not self.data:
            raise ValueError(f"Data cannot be empty")
        if sorted(self.data.keys()) != sorted(self.I):
            raise ValueError(f"Data keys are not {self.I}")
        for datum in self.data.values():
            if not isinstance(datum, numeric_types):
                raise ValueError(f"Data {type(datum)} is not {numeric_types}")

    def __getitem__(self, i:tp.Union[int, slice]) -> object:
        I = self.I[self.slice(i)]
        if isinstance(I, int):
            return self.data[I]
        elif isinstance(I, (range, slice)):
            return Vector(data={j:self.data[i] for j, i in self.enumerate(I)}, validate=False)
        raise NotImplementedError(type(I))
    
    def __str__(self) -> str:
        return "\n".join(map(self._value_frmt.format, self.data.values()))

    def __add__(self, other:object) -> object:
        if isinstance(other, numeric_types):
            data = {key:val+other for key, val in self.data.items()}
            return Vector(data=data, validate=False)
        if isinstance(other, Vector):
            if self.n != other.n:
                raise ValueError(f"Incompatible dimensions {self.n} and {other.n}")
            data = {key:val+other[key] for key, val in self.data.items()}
            return Vector(data=data, validate=False)
        raise NotImplementedError(type(other))


    def __iter__(self) -> tp.Iterator:
        for i in self.I:
            yield self.data[i]
        
####################################################################################################

class VariableVector(Vector):
    def __init__(self, name:str, n:int):
        data = {i:Variable(name=f"{name}_{i}") for i in self.range(n)}
        super().__init__(data=data, validate=False)

class ConstantVector(Vector):
    def __init__(self, constant:Numeric, n:int):
        data = {i:constant for i in self.range(n)}
        super().__init__(data=data, validate=False)

class ZeroVector(ConstantVector):
    def __init__(self, n:int):
        super().__init__(constant=0, n=n)

class UnitVector(ConstantVector):
    def __init__(self, n:int):
        return super().__init__(constant=1, n=n)