import typing as tp
from ..expression import Expression

####################################################################################################

numeric_types = (int, float, complex, Expression)
Numeric = tp.Union[int, float, complex, Expression]

class Container:
    value_frmt = "{:}"

    @staticmethod
    def range(n:int) -> range:
        return range(1, n+1)

    @staticmethod
    def enumerate(iterable:tp.Iterable) -> tp.Iterable:
        return enumerate(iterable, start=1)

    def _get_data(self, *args, **kwargs) -> object:
        raise NotImplementedError

    def _get_datum(self, *args, **kwargs) -> Numeric:
        raise NotImplementedError

    def _validate(self) -> None:
        raise NotImplementedError