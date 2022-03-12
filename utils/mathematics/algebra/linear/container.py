# Nicholas Eterovic 2022Q1
####################################################################################################

# Open-source imports.
import typing as tp
 
# In-house imports.
from ..expression import Expression

####################################################################################################

numeric_types = (int, float, complex, Expression)
Numeric = tp.Union[int, float, complex, Expression]

class Container:
    _value_frmt = "{:}"
    
    def __init__(self, data:object, validate:bool=True):
        self.data = self._normalize_data(data=data)
        if validate:
            self._validate_data()
            
    @staticmethod
    def range(n:int) -> range:
        return range(1, n+1)

    @staticmethod
    def enumerate(iterable:tp.Iterable) -> tp.Iterable:
        return enumerate(iterable, start=1)

    @staticmethod
    def slice(i:tp.Union[int, slice]) -> tp.Union[int, slice]:
        if isinstance(i, int):
            if i == 0:
                raise KeyError(i)
            else:
                i -= 1
        elif isinstance(i, slice):
            if i.start is not None:
                i = slice(i.start-1, i.stop, i.step)
        else:
            raise NotImplementedError(i)
        return i
    
    def evaluate(self, **kwargs) -> object:
        data = {key:val.evaluate(**kwargs) for key, val in self.data.items()}
        return self.__class__(data=data)
    
    def _normalize_data(self, *args, **kwargs) -> object:
        raise NotImplementedError

    def _validate_data(self) -> None:
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        if isinstance(other, Container):
            return self.data == other.data
        raise NotImplementedError(type(other))