# Nicholas Eterovic 2022Q1
####################################################################################################

# Open-source imports.
import typing as tp

# In-house imports.
from .vector import *
from ..expression import *

##################################################################################################

class VectorSpace:

    def __init__(self, space:object):
        self.space = space
        assert self.zero in self

    @property
    def zero(self) -> object:
        raise NotImplementedError
    
    def __contains__(self, element:object) -> bool:
        raise NotImplementedError

##################################################################################################

class Span(VectorSpace):

    def __init__(self, *vectors:tp.Tuple[Vector]):
        self.n, = set(vector.n for vector in vectors)
        self.vectors = vectors
        space = sum(
            [vector*Variable(f"c_{i}") for i, vector in Vector.enumerate(vectors)],
            self.zero,
        )
        super().__init__(space=space)

    @property
    def zero(self) -> Vector:
        return ZeroVector(n=self.n)

    def __contains__(self, element:object) -> bool:
        if element == self.zero:
            return True
        raise NotImplementedError

##################################################################################################