# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source packages.
import typing as tp

####################################################################################################

class CollatzTree:
        
    def __init__(self):
        self._term_cache = {1:1}
        self._length_cache = {1:1}

    def get_term(self, n:int=1) -> int:
        if n in self._term_cache:
            return self._term_cache[n]
        term = self._term_cache[n] = n//2 if n%2==0 else 1+3*n
        return term
    
    def get_length(self, n:int=1) -> int:
        if n in self._length_cache:
            return self._length_cache[n]
        term = self.get_term(n=n)
        length = self._length_cache[n] = 1+self.get_length(n=term)
        return length
    
    def get_sequence(self, n:int=1) -> tp.List[int]:
        sequence = [n]
        while n!=1:
            n = self.get_term(n=n)
            sequence.append(n)
        return sequence