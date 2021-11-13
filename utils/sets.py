# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source packages.
import typing as tp
import itertools as it
import functools as ft

####################################################################################################

def get_intersection_sets(sets:tp.List[str]) -> set:
    return ft.reduce(set.intersection, sets, set())

def get_agg_union_sets(sets:tp.List[set], agg:tp.Callable=len) -> int:
    """
    > Aggregate <sets> using the inclusion-exclusion principle.
    """
    n = len(sets)
    I = range(1, n+1)
    count = 0
    for i in I:
        sign = 1 if i%2==1 else -1
        subsets = it.combinations(sets, i)
        intersections = map(get_intersection_sets, subsets)
        counts = map(agg, intersections)
        count += sign*sum(counts, 0)
    return count

