import typing as tp
import functools as ft
from ..expression import Expression

####################################################################################################

numeric_types = (int, float, complex, Expression)
Numeric = tp.Union[int, float, complex, Expression]

class Container:
    _value_frmt = "{:}"
    def __init__(self, get_datum_func:tp.Callable):
        self.get_datum = get_datum_func
    
    @staticmethod
    def range(n:int) -> range:
        return range(1, n+1)

    @staticmethod
    def enumerate(iterable:tp.Iterable) -> tp.Iterable:
        return enumerate(iterable, start=1)

    def evaluate(self, **kwargs) -> object:
        data = {key:val.evaluate(**kwargs) for key, val in self.data.items()}
        return self.__class__(data=data)
    
    def normalize_data(self, *args, **kwargs) -> object:
        raise NotImplementedError

    def _get_datum(self, *args, **kwargs) -> Numeric:
        raise NotImplementedError

    def validate(self) -> None:
        raise NotImplementedError