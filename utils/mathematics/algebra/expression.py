# Nicholas Eterovic 2022Q1
####################################################################################################

class Expression:
    def __init__(self, **children):
        self._children = children

    def evaluate(self, **kwargs):
        children = {}
        for name, child in self._children.items():
            if isinstance(child, Expression):
                child = child.evaluate(**kwargs)
            children[name] = child
        return self.__class__(**children)

    def __eq__(self, other) -> bool:
        raise NotImplementedError(type(other))
    
    def __neg__(self):
        return Negation(child=self)
    
    def __add__(self, other):
        return Sum(left=self, right=other)

    def __radd__(self, other):
        return Sum(left=other, right=self)

    def __sub__(self, other):
        return Difference(left=self, right=other)

    def __rsub__(self, other):
        return Difference(left=other, right=self)
    
    def __mul__(self, other):
        return Multiplication(left=self, right=other)

    def __rmul__(self, other):
        return Multiplication(left=other, right=self)

class Variable(Expression):
    def __init__(self, name:str):
        super().__init__(name=name)

    @property
    def name(self) -> str:
        return self._children["name"]
    
    def evaluate(self, **kwargs) -> Expression:
        if self.name in kwargs:
            return kwargs[self.name]
        return self
    
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.name.__eq__(other.name)
        raise NotImplementedError(type(other))
    
    def __str__(self) -> str:
        return self.name

####################################################################################################

class UnaryExpression(Expression):
    def __init__(self, child:object):
        super().__init__(child=child)

    @property
    def child(self):
        return self._children["child"]
    
class Negation(UnaryExpression):
    
    def evaluate(self, **kwargs):
        expression = super().evaluate(**kwargs)
        return Multiplication(left=-1, right=expression.child).evaluate(**kwargs)

    def __str__(self) -> str:
        return f"-{self.child}"

####################################################################################################

class BinaryExpression(Expression):
    def __init__(self, left:object, right:object):
        super().__init__(left=left, right=right)

    @property
    def left(self):
        return self._children["left"]

    @property
    def right(self):
        return self._children["right"]
        
class Sum(BinaryExpression):

    def evaluate(self, **kwargs) -> Expression:
        expression = super().evaluate(**kwargs)
        if expression.left == 0:
            return expression.right
        if expression.right == 0:
            return expression.left
        return expression.left + expression.right
    
    def __str__(self) -> str:
        return f"{self.left} + {self.right}"

class Difference(BinaryExpression):

    def evaluate(self, **kwargs) -> Expression:
        expression = super().evaluate(**kwargs)
        if expression.left == 0:
            return Negation(child=expression.right)
        if expression.left == expression.right:
            return 0
        if expression.right == 0:
            return expression.left
        return expression.left - expression.right

    def __str__(self) -> str:
        return f"{self.left} - {self.right}"

class Multiplication(BinaryExpression):

    def evaluate(self, **kwargs):
        expression = super().evaluate(**kwargs)
        if expression.left == 0:
            return 0
        if expression.right == 0:
            return 0
        if expression.left == 1:
            return expression.right
        if expression.right == 1:
            return expression.left
        return self.left * self.right

    def __str__(self) -> str:
        expression = super().evaluate()
        return f"{self.left} * {self.right}"

####################################################################################################