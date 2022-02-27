# Nicholas Eterovic 2022Q1
####################################################################################################

# Open-source imports.
import math
import typing as tp
import operator as op
import itertools as it
import functools as ft

# In-house imports.
from .vector import Vector
from ..expression import Variable
from .container import Container, Numeric, numeric_types

##################################################################################################

def check_is_square(func:tp.Callable) -> tp.Callable:
    @ft.wraps(func)
    def wrapped(self, *args, **kwargs) -> object:
        if not self.is_square:
            raise NotImplemented(f"Matrix is not square")
        return func(self, *args, **kwargs)
    return wrapped

class Matrix(Container):
    def __init__(self, data:object, validate:bool=True):
        self.data = self._normalize_data(data=data)
        if validate:
            self._validate_data()
    
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
    def rows(self) -> tp.Iterable[Vector]:
        J = list(self.J)
        return (Vector(data=[self.data[(i, j)] for j in J]) for i in self.I)

    @property
    def cols(self) -> tp.Iterable[Vector]:
        I = list(self.I)
        return (Vector(data=[self.data[(i, j)] for i in I]) for j in self.J)
    
    @property
    def T(self) -> object:
        keys = ((j, i) for i, j in self.data.keys())
        vals = self.data.values()
        data = dict(zip(keys, vals))
        return self.__class__(data=data, validate=False)

    @property
    def is_square(self) -> bool:
        return self.n == self.m
    
    @property
    def is_symmetric(self) -> bool:
        if not self.is_square:
            return False
        return self == self.T

    @property
    def is_skew_symmetric(self) -> bool:
        if not self.is_square:
            return False
        return self == - self.T
    
    @property
    def LU(self) -> tp.Tuple[object, object]:
        U, ops = get_row_echelon_form(M=self)
        inv_ops = [op.inv() for op in ops]
        L = ft.reduce(op.mul, inv_ops, IdentityMatrix(n=U.n))
        return L, U
    
    @property
    def LDV(self) -> tp.Tuple[object, object, object]:
        L, U = self.LU
        V, ops = get_reduced_row_echelon_form(M=U)
        inv_ops = [op.inv() for op in ops]
        D = ft.reduce(op.mul, inv_ops, IdentityMatrix(n=U.n))
        return L, D, V

##################################################################################################
    
    @check_is_square
    def inv(self) -> object:
        raise NotImplementedError

##################################################################################################

    @staticmethod
    def _normalize_data(data:object) -> tp.Dict[tp.Tuple[int, int], Numeric]:
        if isinstance(data, dict):
            return data
        if isinstance(data, tp.Iterable):
            if all(isinstance(row, tp.Iterable) for row in data):
                return {
                    (i, j):datum
                    for i, row in Container.enumerate(data)
                    for j, datum in Container.enumerate(row)
                }
        raise NotImplementedError(type(data))

    def _validate_data(self) -> None:
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
    
    def __neg__(self) -> object:
        return self * -1
    
    def __add__(self, other) -> object:
        if isinstance(other, numeric_types):
            data = {key:other+val for key, val in self.data.items()}
            return Matrix(data=data, validate=False)
        if isinstance(other, Matrix):
            if (self.n, self.m) != (other.n, other.m):
                raise 
            if self.m != other.n:
                raise ValueError(f"Incompatible dimensions {self.m} and {other.n}")
            data = {}
            for key, val in it.chain(self.data.items(), other.data.items()):
                if key not in data:
                    data[key] = val
                else:
                    data[key] += val
            return Matrix(data=data, validate=False)
        raise NotImplementedError(type(other))
        
    def __mul__(self, other) -> object:
        if isinstance(other, numeric_types):
            data = {key:other*val for key, val in self.data.items()}
            return Matrix(data=data, validate=False)
        if isinstance(other, Vector):
            if self.m != other.n:
                raise ValueError(f"Incompatible dimensions {self.m} and {other.n}")
            data = [row*other for row in self.rows]
            return Vector(data=data, validate=False)
        if isinstance(other, Matrix):
            if self.m != other.n:
                raise ValueError(f"Incompatible dimensions {self.m} and {other.n}")
            data = [[row*col for col in other.cols] for row in self.rows]
            return Matrix(data=data, validate=False)
        raise NotImplementedError(type(other))

    def __add__(self, other) -> object:
        return self.add(other=other)
    
    def __getitem__(self, arg:tp.Tuple[tp.Union[int, slice]]) -> object:
        i, j = arg
        I = self.I[self.slice(i)]
        J = self.J[self.slice(j)]
        if isinstance(I, int):
            if isinstance(J, int):
                return self.data[(i, j)]
            elif isinstance(J, (range, slice)):
                data = {l:self.data[(i, j)] for l, j in self.enumerate(J)}
                return Vector(data=data, validate=False)
        elif isinstance(I, (range, slice)):
            if isinstance(J, int):
                data = {k:self.data[(i, j)] for k, i in self.enumerate(I)}
                return Vector(data=data, validate=False)
            elif isinstance(J, (range, slice)):
                data = {(k, l):self.data[(i, j)] for k, i in self.enumerate(I) for l, j in self.enumerate(J)}
                return Matrix(data=data, validate=False)
        raise ValueError(type(I), type(J))
            
    def __str__(self) -> str:
        matrix_str = ""
        I = list(self.I)
        J = list(self.J)
        for i in I:
            row_values = (self.data[(i, j)] for j in J)
            row_str = " ".join(map(self._value_frmt.format, row_values))
            matrix_str += row_str + "\n"
        return matrix_str
        
##################################################################################################

class VariableMatrix(Matrix):
    def __init__(self, name:str, n:int, m:int=None):
        self.name = name
        if m is None:
            m = n
        data = {}
        for i, j in it.product(self.range(n), self.range(m)):
            data[(i, j)] = Variable(name=f"{name}_{i}_{j}")
        return super().__init__(data=data, validate=False)

class IdentityMatrix(Matrix):
    def __init__(self, n:int, m:int=None):
        if m is None:
            m = n
        data = {}
        for i, j in it.product(self.range(n), self.range(m)):
            data[(i, j)] = int(i==j)
        return super().__init__(data=data, validate=False)

    @check_is_square
    def inv(self):
        return self

class PermuterMatrix(Matrix):
    """
    Premultiply (postmultiply) to swap row (column) i with row (column) j.
    """
    def __init__(self, ri:int, rj:int, n:int, m:int=None):
        self.i = i
        self.j = j
        if m is None:
            m = n
        data = {}
        for i, j in it.product(self.range(n), self.range(m)):
            if i == self.i:
                data[(i, j)] = int(j==self.j)
            elif i == self.j:
                data[(i, j)] = int(j==self.i)
            else:
                data[(i, j)] = int(i==j)
        return super().__init__(data=data, validate=False)

    def inv(self):
        return PermuterMatrix(i=self.i, j=self.j, n=self.n, m=self.m)

class MultiplierMatrix(Matrix): 
    """
    Premultiply (postmultiply) to multiply row (column) i by a constant.
    """
    def __init__(self, i:int, constant:Numeric, n:int, m:int=None):
        self.i = i
        self.constant = constant
        if m is None:
            m = n
        data = {}
        for i, j in it.product(self.range(n), self.range(m)):
            if (i, j) == (self.i, self.i):
                data[(i, j)] = constant
            else:
                data[(i, j)] = int(i==j)
        return super().__init__(data=data, validate=False)

    def inv(self):
        return MultiplierMatrix(i=self.i, constant=1/self.constant, n=self.n, m=self.m)

class AdderMatrix(Matrix):
    """
    Premultiply to add row j multiplied by a constant to row i.
    """
    def __init__(self, i:int, j:int, constant:Numeric, n:int, m:int=None):
        self.i = i
        self.j = j
        self.constant = constant
        if m is None:
            m = n
        data = {}
        for i, j in it.product(self.range(n), self.range(m)):
            if (i, j) == (self.i, self.j):
                if i == j:
                    data[(i, j)] = 1 + constant
                else:
                    data[(i, j)] = constant
            else:
                data[(i, j)] = int(i==j)
        return super().__init__(data=data, validate=False)

    def inv(self):
        return AdderMatrix(i=self.i, j=self.j, constant=-self.constant, n=self.n, m=self.m)

class RotatorMatrix(Matrix):
    """
    Premultiply to rotate by radians about the origin.
    """
    def __init__(self, radians:float, n:int):
        if n == 2:
            cos = math.cos(radians)
            sin = math.sin(radians)
            data = [
                [+cos, -sin],
                [+sin, +cos],
            ]
            return super().__init__(data=data, validate=False)
        raise NotImplementedError(n)

    def inv(self):
        return RotatorMatrix(radians=-self.radians, n=self.n)

##################################################################################################

def get_row_echelon_form(M:Matrix) -> tp.Tuple[Matrix, tp.List[Matrix]]:
    """
    Returns:
        Matrix, input matrix transformed to row-echelon form.
        List of Matrix, sequence of applied elementary operations.
    """
    i = 1
    j = 1
    n = M.n
    m = M.m
    ops = []
    while i <= n and j <= m:
        vals = M[i:n, j]
        pivot = max(vals, key=abs, default=0)
        if pivot == 0:
            j += 1
            continue
        k = min(k for k, x in enumerate(vals, i) if x == pivot)
        if k != i:
            # Swap rows so that largest non-zero value is in pivot position.
            P = PermuterMatrix(ri=i, rj=k, n=n)
            M = P * M
            ops.append(P)
        # For each row below the pivot row
        vals = M[i+1:n, j]
        for k, val in enumerate(vals, i+1):
            # Subtract scaled pivot row to eliminate leading value. 
            if val == 0:
                continue
            q = - val / pivot
            A = AdderMatrix(ri=k, rj=i, constant=q, n=n)
            M = A * M
            ops.append(A)
        i += 1
        j += 1
    return M, ops

def get_reduced_row_echelon_form(M:Matrix) -> tp.Tuple[Matrix, tp.List[Matrix]]:
    """
    Returns:
        Matrix, input matrix transformed to reduced-row-echelon form.
        List of Matrix, sequence of applied elementary operations.
    """
    M, ops = get_row_echelon_form(M=M)
    for i, row in enumerate(M.rows, 1):
        pivot = row.pivot
        if pivot is None:
            continue
        D = MultiplierMatrix(ri=i, constant=1/pivot, n=M.n)
        M = D * M
        ops.append(D)
    return M, ops