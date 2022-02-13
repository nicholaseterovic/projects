


class Expression:
    
    def evaluate(**kwargs):
        raise NotImplementedError

    def __add__(self, other):
        return Sum(left=self, right=other)

    def __radd__(self, other):
        return Sum(left=other, right=self)

    def __sub__(self, other):
        return Difference(left=self, right=other)

    def __rsub__(self, other):
        return Difference(left=other, right=self)

    def __mul__(self, other):
        return Multiply(left=self, right=other)

    def __rmul__(self, other):
        return Multiply(left=other, right=self)

    def __eq__(self, other) -> False:
        try:
            return self.evaluate() == other.evaluate()
        except:
            pass
        return False

class Variable(Expression):
    def __init__(self, name:str):
        self.name = name

    def __eq__(self, other):
        return 

    def evaluate(self, **kwargs) -> Expression:
        if self.name in kwargs:
            return kwargs[self.name]
        return self
    
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.name.__eq__(other.name)
        return super().__eq__(other)
    
    def __str__(self) -> str:
        return self.name

class BinaryExpression(Expression):
    def __init__(self, left:object, right:object):
        self.left = left
        self.right = right

class Sum(BinaryExpression):

    def evaluate(self, **kwargs) -> Expression:
        try:
            if self.left == 0:
                return self.right
            if self.right == 0:
                return self.left
        except:
            pass
        return self.left.evaluate(**kwargs) + self.right.evaluate(**kwargs)

    def __str__(self) -> str:
        return f"{self.left} + {self.right}"

class Difference(BinaryExpression):

    def evaluate(self, **kwargs) -> Expression:
        try:
            if self.left == self.right:
                return 0
        except:
            pass
        return self.left.evaluate(**kwargs) - self.right.evaluate(**kwargs)

    def __str__(self) -> str:
        return f"{self.left} - {self.right}"

class Multiply(BinaryExpression):

    def evaluate(self, **kwargs):
        try:
            if self.left == 0:
                return 0
            if self.right == 0:
                return 0
            if self.left == 1:
                return self.right.evaluate()
            if self.right == 1:
                return self.left.evaluate()
        except:
            pass
        return self.left.evaluate(**kwargs) - self.right.evaluate(**kwargs)

    def __str__(self) -> str:
        return f"{self.left} * {self.right}"