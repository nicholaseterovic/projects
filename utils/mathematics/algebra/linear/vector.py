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
        self.data = self.normalize_data(data=data)
        if validate:
            self.validate()
    
    @property
    def n(self) -> int:
        return len(self.data)
    
    @property
    def I(self) -> tp.Iterator[int]:
        return self.range(self.n)
    
    @staticmethod
    def normalize_data(data:object) -> tp.Dict[int, Numeric]:
        if isinstance(data, dict):
            return data
        if isinstance(data, tp.Iterable):
            return {i:datum for i, datum in Container.enumerate(data)}
        raise ValueError
    
    def validate(self) -> None:
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
        return "\n".join(map(self._value_frmt.format, self.data.values()))

    def __mul__(self, other:object) -> object:
        if isinstance(other, Vector):
            if self.n != other.n:
                raise ValueError(f"Lengths {self.n} and {other.n} are not equal")
            return sum(self.data[i]*other.data[i] for i in self.I)
        raise NotImplementedError(type(other))

    @classmethod
    def variable(cls, name:str, n:int):
        data = {i:Variable(name=f"{name}_{i}") for i in cls.range(n)}
        return cls(data=data, validate=False)

    @classmethod
    def constant(cls, constant:Numeric, n:int):
        data = {i:constant for i in cls.range(n)}
        return cls(data=data, validate=False)

    @classmethod
    def zero(cls, n:int):
        return cls.constant(constant=0, n=0)

    @classmethod
    def unit(cls, n:int):
        return cls.constant(constant=1, n=0)