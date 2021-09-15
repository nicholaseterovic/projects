# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import typing as tp
import functools as ft
import itertools as it

def get_union_agg(sets:tp.List[set], agg:tp.Callable=len) -> int:
    # Aggregate sets using inclusion-exclusion principle.
    get_intersection = lambda sets:ft.reduce(set.intersection, sets)
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

def solution_001(n:int=1000, K:tp.List[int]=[3, 5], agg=sum):
    sets = [set(range(k, n, k)) for k in K]
    solution = get_union_agg(sets=sets, agg=agg)
    return solution

    
    


