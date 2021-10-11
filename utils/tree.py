# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source packages.
import typing as tp

####################################################################################################

class Node:

    def __init__(self, val:int, children:tp.List=[]):
        self.val = val
        self.children = children

    @classmethod
    def from_triangle_matrix(cls, triangle_matrix:tp.List[tp.List[int]]):
        for i, row in enumerate(reversed(triangle_matrix)):
            if i==0:
                nodes = [cls(val=val, children=[]) for val in row]
            else:
                nodes = [cls(val=val, children=[nodes[i], nodes[i+1]]) for i, val in enumerate(row)]
        return nodes[0]

    @property
    def maximal_path(self) -> tp.List[int]:
        child_maximal_paths = [child.maximal_path for child in self.children]
        return [self.val, *max(child_maximal_paths, default=[], key=sum)]