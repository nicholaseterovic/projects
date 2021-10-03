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

def prod(container:tp.Container, default=1) -> int:
    iterator = iter(container)
    try:
        first = next(iterator)
    except StopIteration:
        return default
    return first*ft.reduce(type(first).__mul__, iterator, 1)

def solution_004(numbers:int=2, digits:int=3) -> int:
    rng = range(int("9"*digits), int("1"*digits)-1, -1)
    nums = it.product(rng, repeat=numbers)
    max_palindrome = -math.inf
    for num in nums:
        if any(n<m for n, m in zip(num[:-1], num[1:])):
            continue
        val = prod(num)
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
    powered = [prime**power for prime, power in max_powers]
    lcm = prod(powered)
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
    num_list = [int(num) for num in num_str]
    num_sublists = [num_list[i:i+n] for i in range(0, len(num_list)+1-n)]
    max_prod = -math.inf
    for num_sublist in num_sublists:
        if max_prod>-math.inf and 0 in num_sublist:
            continue
        num_subiter = filter(int(1).__ne__, num_sublist)
        prod_num = prod(num_subiter, default=1)
        if prod_num>max_prod:
            max_prod = prod_num
    return max_prod

####################################################################################################

def get_pythag_triples(perimeter:int) -> tp.List[tp.Tuple[int, int, int]]:
    """
    > Return Pythagorian triple(s) (a, b, c) such that:
      a^2 + b^2 = c^2
      a + b + c = perimeter
      a < b < c
    """
    pythag_triples = []
    for a in range(1, perimeter//3):
        for b in range(a+1, 1+(perimeter-a)//2):
            c = perimeter - a - b
            if a**2 + b**2 == c**2:
                pythag_triple = (a, b, c)
                pythag_triples.append(pythag_triple)
    return pythag_triples

def solution_009(perimeter:int=1000) -> int:
    pythag_triples = get_pythag_triples(perimeter=perimeter)
    a, b, c = max(pythag_triples)
    return a*b*c

####################################################################################################

def solution_010(n:int=2e6) -> int:
    return sum(primes(max_val=n))

####################################################################################################

def get_max_adj_prod(matrix:tp.List[tp.List[int]], adj_num:int) -> int:
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    I = len(matrix)
    J = min(map(len, matrix), default=0)
    max_adj_prod = -math.inf
    for i in range(I):
        for j in range(J):
            for di, dj in directions:
                if 0<=i+(adj_num-1)*di<I and 0<=j+(adj_num-1)*dj<J:
                    adj = (matrix[i+step*di][j+step*dj] for step in range(adj_num))
                    adj_prod = prod(adj)
                    if adj_prod>max_adj_prod:
                        max_adj_prod = adj_prod
    return max_adj_prod

def solution_011(adj_num:int=4) -> int:
    matrix_str = """
    08 02 22 97 38 15 00 40 00 75 04 05 07 78 52 12 50 77 91 08
    49 49 99 40 17 81 18 57 60 87 17 40 98 43 69 48 04 56 62 00
    81 49 31 73 55 79 14 29 93 71 40 67 53 88 30 03 49 13 36 65
    52 70 95 23 04 60 11 42 69 24 68 56 01 32 56 71 37 02 36 91
    22 31 16 71 51 67 63 89 41 92 36 54 22 40 40 28 66 33 13 80
    24 47 32 60 99 03 45 02 44 75 33 53 78 36 84 20 35 17 12 50
    32 98 81 28 64 23 67 10 26 38 40 67 59 54 70 66 18 38 64 70
    67 26 20 68 02 62 12 20 95 63 94 39 63 08 40 91 66 49 94 21
    24 55 58 05 66 73 99 26 97 17 78 78 96 83 14 88 34 89 63 72
    21 36 23 09 75 00 76 44 20 45 35 14 00 61 33 97 34 31 33 95
    78 17 53 28 22 75 31 67 15 94 03 80 04 62 16 14 09 53 56 92
    16 39 05 42 96 35 31 47 55 58 88 24 00 17 54 24 36 29 85 57
    86 56 00 48 35 71 89 07 05 44 44 37 44 60 21 58 51 54 17 58
    19 80 81 68 05 94 47 69 28 73 92 13 86 52 17 77 04 89 55 40
    04 52 08 83 97 35 99 16 07 97 57 32 16 26 26 79 33 27 98 66
    88 36 68 87 57 62 20 72 03 46 33 67 46 55 12 32 63 93 53 69
    04 42 16 73 38 25 39 11 24 94 72 18 08 46 29 32 40 62 76 36
    20 69 36 41 72 30 23 88 34 62 99 69 82 67 59 85 74 04 36 16
    20 73 35 29 78 31 90 01 74 31 49 71 48 86 81 16 23 57 05 54
    01 70 54 71 83 51 54 69 16 92 33 48 61 43 52 01 89 19 67 48
    """
    matrix = [
        [int(num_str) for num_str in row_str.strip().split(" ")]
        for row_str in matrix_str.strip().split("\n")
    ]
    return get_max_adj_prod(matrix=matrix, adj_num=adj_num)

####################################################################################################

def triangle_numbers(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    """
    > Yield triangle numbers.
    """
    idx = 1
    val = 1
    triangle_numbers = []
    exceeded_max = False
    while not exceeded_max:
        if idx>max_idx:
            exceeded_max = True
        elif val>max_val:
            exceeded_max = True
        else:
            val = idx*(idx+1)//2
            idx += 1
            yield val

def get_factors(n:int) -> tp.List[int]:
    prime_decomposition = get_prime_decomposition(n=n)
    factors = set([1, n])
    for r in range(1, len(prime_decomposition)):
        for primes in set(it.combinations(prime_decomposition, r=r)):
            factor = prod(primes, default=1)
            factors.add(factor)
    return sorted(factors)
    
def solution_012(min_num_factors:int=500) -> int:
    for triangle_number in triangle_numbers():
        factors = get_factors(triangle_number)
        num_factors = len(factors)
        if num_factors>min_num_factors:
            return triangle_number

####################################################################################################

def solution_013() -> int:
    raise NotImplementedError

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

def solution_014(max_num:int=1e6) -> int:
    nums = range(1, int(max_num))
    collatz_tree = CollatzTree()
    return max(nums, key=collatz_tree.get_length)

####################################################################################################
