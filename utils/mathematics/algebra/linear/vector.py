# Nicholas Eterovic 2022Q1
####################################################################################################

# Open-source imports.
import typing as tp
import itertools as it

# In-house imports.
from ..expression import Variable
from .container import Container, Numeric, numeric_types

####################################################################################################

class Vector(Container):

    def __init__(self, data:object, validate:bool=True):
        self.data = self._normalize_data(data=data)
        if validate:
            self._validate_data()
    
    @property
    def n(self) -> int:
        return len(self.data)
    
    @property
    def I(self) -> tp.Iterator[int]:
        return self.range(self.n)
    
    @property
    def pivot(self) -> tp.Union[Numeric, None]:
        for i in self.I:
            if self.data[i] != 0:
                return i
        return None

    def dot(self, other:object) -> object:
        if isinstance(other, numeric_types):
            data = {key:other*val for key, val in self.data.items()}
            return Vector(data=data, validate=False)
        if isinstance(other, Vector):
            if self.n != other.n:
                raise ValueError(f"Incompatible dimensions {self.n} and {other.n}")
            return sum(self.data[i]*other.data[i] for i in self.I)
        raise NotImplementedError(type(other))
    
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
        elif isinstance(I, slice):
            return Vector(data={i:self.data[i] for i in I}, validate=False)
        raise NotImplementedError(type(I))
    
    def __str__(self) -> str:
        return "\n".join(map(self._value_frmt.format, self.data.values()))

    def __mul__(self, other:object) -> object:
        return self.dot(other=other)
        
####################################################################################################

    @classmethod
    def Variable(cls, name:str, n:int):
        data = {i:Variable(name=f"{name}_{i}") for i in cls.range(n)}
        return cls(data=data, validate=False)

    @classmethod
    def Constant(cls, constant:Numeric, n:int):
        data = {i:constant for i in cls.range(n)}
        return cls(data=data, validate=False)

    @classmethod
    def Zero(cls, n:int):
        return cls.constant(constant=0, n=n)

    @classmethod
    def Unit(cls, n:int):
        return cls.constant(constant=1, n=n)