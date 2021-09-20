# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import math
from operator import pos
import typing as tp
import functools as ft
import itertools as it

####################################################################################################

def get_set_union_agg(sets:tp.List[set], agg:tp.Callable=len) -> int:
    '''
    > Aggregate sets using inclusion-exclusion principle.
    '''
    get_intersection = lambda sets:ft.reduce(set.intersection, sets, set())
    n = len(sets)
    I = range(1, n+1)
    count = 0
    for i in I:
        sign = 1 if i%2==1 else -1
        subsets = it.combinations(sets, i)
        intersections = map(get_intersection, subsets)
        counts = map(agg, intersections)
        count += sign*sum(counts, 0)
    return count

def solution_001(n:int=1000, K:tp.List[int]=[3, 5], agg=sum) -> int:
    sets = [set(range(k, n, k)) for k in K]
    solution = get_set_union_agg(sets=sets, agg=agg)
    return solution

####################################################################################################

def even_fibonnaci_numbers(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    idx = 1
    prev = 2
    curr = 8
    exceeded_max = False
    while not exceeded_max:
        if idx>max_idx:
            exceeded_max = True
        else:
            if idx==1:
                val = prev
            elif idx==2:
                val = curr
            else:
                val = 4*curr+prev
                prev = curr
                curr = val
            if val>max_val:
                exceeded_max = True
            else:
                yield val
        idx += 1

def solution_002(max_val:int=4e6) -> int:
    return sum(even_fibonnaci_numbers(max_val=max_val), 0)

####################################################################################################

def primes(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    idx = 1
    val = 2
    primes = []
    exceeded_max = False
    while not exceeded_max:
        if idx>max_idx:
            exceeded_max = True
        elif val>max_val:
            exceeded_max = True
        elif not any(val%prime==0 for prime in primes):
            primes.append(val)
            idx += 1
            yield val
        val += 1

def get_prime_decomposition(n:int) -> tp.Container[int]:
    for prime in primes(max_val=int(n**0.5)):
        if n%prime==0:
            return [prime, *get_prime_decomposition(n//prime)]
    return [n]

def solution_003(n:int=600851475143) -> int:
    return max(get_prime_decomposition(n=n))

####################################################################################################    