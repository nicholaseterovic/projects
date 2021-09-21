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

def solution_001(n:int=1000, K:tp.List[int]=[3, 5], agg=sum) -> int:
    sets = [set(range(k, n, k)) for k in K]
    solution = get_set_union_agg(sets=sets, agg=agg)
    return solution

####################################################################################################

def even_fibonnaci_numbers(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    """
    > Yield even Fibonacci numbers.
    """
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
    """
    > Yield prime numbers using the Sieve of Eratosthenes.
    """
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
    """
    > Decompose <n> into its prime factors.
    """
    for prime in primes(max_val=int(n**0.5)):
        if n%prime==0:
            return [prime, *get_prime_decomposition(n//prime)]
    return [n]

def solution_003(n:int=600851475143) -> int:
    return max(get_prime_decomposition(n=n))

####################################################################################################

def solution_004(numbers:int=2, digits:int=3) -> int:
    rng = range(int("9"*digits), int("1"*digits)-1, -1)
    nums = it.product(rng, repeat=numbers)
    max_palindrome = -math.inf
    for num in nums:
        if any(n<m for n, m in zip(num[:-1], num[1:])):
            continue
        val = ft.reduce(int.__mul__, num, 1)
        val_str = str(val)
        if val_str==val_str[::-1] and val>max_palindrome:
            max_palindrome = val
    return max_palindrome

####################################################################################################

def get_lcm(*numbers:tp.Collection[int]) -> int:
    """
    Compute the lowest common multiple of <numbers>.
    """
    decomps = [get_prime_decomposition(n) for n in numbers]
    powers = [(prime, len(list(group))) for decomp in decomps for prime, group in it.groupby(decomp)]
    powers = sorted(powers, key=lambda x:x[0])
    max_powers = [max(power) for prime, power in it.groupby(powers, key=lambda x:x[0])]
    lcm = ft.reduce(int.__mul__, [prime**power for prime, power in max_powers], 1)
    return lcm

def solution_005(n:int=20) -> int:
    return get_lcm(*range(1, n+1))

####################################################################################################

def get_sum_of_powers(n:int, power:int=1) -> int:
    """
    Compute the sum of the first <n> natural numbers raised to <power>.
    """
    if power==1:
        return n*(n+1)//2
    elif power==2:
        return n*(n+1)*(2*n+1)//6
    else:
        return sum(k**power for k in range(1, n+1))

def solution_006(n:int=100) -> int:
    sum_of_squares = get_sum_of_powers(n=n, power=2)
    square_of_sum = get_sum_of_powers(n=n, power=1)**2
    return abs(sum_of_squares-square_of_sum)

####################################################################################################

def solution_007(i:int=10001) -> int:
    for prime in primes(max_idx=i):
        pass
    return prime

####################################################################################################

def solution_008(n:int=13) -> int:
    num_str = """
    73167176531330624919225119674426574742355349194934
    96983520312774506326239578318016984801869478851843
    85861560789112949495459501737958331952853208805511
    12540698747158523863050715693290963295227443043557
    66896648950445244523161731856403098711121722383113
    62229893423380308135336276614282806444486645238749
    30358907296290491560440772390713810515859307960866
    70172427121883998797908792274921901699720888093776
    65727333001053367881220235421809751254540594752243
    52584907711670556013604839586446706324415722155397
    53697817977846174064955149290862569321978468622482
    83972241375657056057490261407972968652414535100474
    82166370484403199890008895243450658541227588666881
    16427171479924442928230863465674813919123162824586
    17866458359124566529476545682848912883142607690042
    24219022671055626321111109370544217506941658960408
    07198403850962455444362981230987879927244284909188
    84580156166097919133875499200524063689912560717606
    05886116467109405077541002256983155200055935729725
    71636269561882670428252483600823257530420752963450
    """
    num_str = "".join(num_str.split())
    subnums_str = [num_str[i:i+n] for i in range(0, len(num_str)+1-n)]
    max_prod = -math.inf
    for subnum_str in subnums_str:
        if "0" in subnum_str and max_prod>-math.inf:
            continue
        subnum =  map(int, subnum_str.replace("1", ""))
        prod = ft.reduce(int.__mul__, subnum, 1)
        if prod>max_prod:
            max_prod = prod
    return max_prod

####################################################################################################