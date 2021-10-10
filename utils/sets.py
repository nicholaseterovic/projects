# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source packages.
import typing as tp
import functools as ft

####################################################################################################

def get_set_union_agg(sets:tp.List[set], agg:tp.Callable=len) -> int:
    """
    > Aggregate <sets> using the inclusion-exclusion principle.
    """
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

