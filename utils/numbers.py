# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source packages.
import math
import typing as tp
import functools as ft
import itertools as it

####################################################################################################

def even_fibonnaci_numbers(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    """
    Arguments:
        max_idx, positive integer: inclusive upper-bound for sequence index.
        max_val, positive integer: inclusive upper-bound for sequence value.
    Returns:
        Generator for even fibonacci numbers.
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
    raise StopIteration

def primes(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    """
    Arguments:
        max_idx, positive integer: inclusive upper-bound for sequence index.
        max_val, positive integer: inclusive upper-bound for sequence value.
    Returns:
        Generator for prime numbers.
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

def get_prime_decomposition(n:int) -> tp.List[int]:
    """
    Arguments:
        n, positve integer: positive integer to decompose.
    Returns:
        List of ascending prime factors of <n>.
    """
    for prime in primes(max_val=int(n**0.5)):
        if n%prime==0:
            return [prime, *get_prime_decomposition(n//prime)]
    return [n]

def prod(container:tp.Container[object], default:object=1) -> object:
    """
    Arguments:
        container, container of object: elements to take product of.
        default, object: the value to return if the container is empty.
    Returns:
        Product of all elements in <container>.
    """
    iterator = iter(container)
    try:
        first = next(iterator)
    except StopIteration:
        return default
    return first*ft.reduce(type(first).__mul__, iterator, 1)

def get_lcm(*numbers:tp.Collection[int]) -> int:
    """
    Arguments:
        numbers, integer arg(s).
    Returns:
        Lowest common multiple of <numbers>.
    """
    decomps = [get_prime_decomposition(n) for n in numbers]
    powers = [(prime, len(list(group))) for decomp in decomps for prime, group in it.groupby(decomp)]
    powers = sorted(powers, key=lambda x:x[0])
    max_powers = [max(power) for prime, power in it.groupby(powers, key=lambda x:x[0])]
    powered = [prime**power for prime, power in max_powers]
    lcm = prod(powered)
    return lcm

def get_sum_of_powers(n:int, power:tp.Union[int, float]=1) -> int:
    """
    Arguments:
        n, positive integer.
        power, number.
    Returns:
        Sum of the first <n> natural numbers each raised to <power>.
    """
    if power==1:
        return n*(n+1)//2
    elif power==2:
        return n*(n+1)*(2*n+1)//6
    else:
        return sum(k**power for k in range(1, n+1))

def get_pythag_triples(perimeter:int) -> tp.List[tp.Tuple[int, int, int]]:
    """
    Arguments:
        perimeter, positive integer: perimeter of Pythagorian triangles.
    Returns:
        Pythagorian triple(s) (a, b, c) such that:
        a^2 + b^2 = c^2
        a + b + c = <perimeter>
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

def get_max_adj_prod(
    matrix:tp.List[tp.List[tp.Union[int, float]]],
    adj_num:int,
    directions:tp.List[tp.Tuple[int, int]]=[(1, 0), (0, 1), (1, 1), (-1, 1)],
) -> int:
    """
    Arguments:
        matrix, list of list of number:
        adj_num, non-negative integer: length of number lines.
        directions, list of step direction: e.g right (1, 0), down (0, 1), ...
    Returns:
        Maximum number-line product in <matrix>.
    """
    I = len(matrix)
    J = min(map(len, matrix), default=0)
    max_adj_prod = -math.inf
    for i in range(I):
        for j in range(J):
            for di, dj in directions:
                if 0<=i+(adj_num-1)*di<I and 0<=j+(adj_num-1)*dj<J:
                    adj = (matrix[i+step*di][j+step*dj] for step in range(adj_num))
                    adj_prod = nu.prod(adj)
                    if adj_prod>max_adj_prod:
                        max_adj_prod = adj_prod
    return max_adj_prod

def triangle_numbers(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    """
    Arguments:
        max_idx, positive integer: inclusive upper-bound for sequence index.
        max_val, positive integer: inclusive upper-bound for sequence value.
    Returns:
        Generator for triangle numbers.
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

def get_divisors(n:int) -> tp.List[int]:
    """
    Arguments:
        n, positive integer.
    Returns:
        List of divisors of <n>.
    """
    prime_decomposition = get_prime_decomposition(n=n)
    divisors = {1, n}
    for r in range(1, len(prime_decomposition)):
        for primes in set(it.combinations(prime_decomposition, r=r)):
            divisor = prod(primes, default=1)
            divisors.add(divisor)
    return sorted(divisors)

def sum_digit_lists(digit_lists:tp.List[tp.List[int]]) -> tp.List[int]:
    """
    Arguments:
        digit_lists: list of numbers, each represented as tuple-of-digits.
    Returns:
        Sum of numbers, represented as tuple-of-digits.
    """
    digit_lists_reversed = it.zip_longest(*map(reversed, digit_lists))
    total_digit_list = []
    carry = 0
    digits = True
    while digits or carry:
        digits = next(digit_lists_reversed, [])
        total_digit_sum = sum(digits, 0) + carry
        total_digit = total_digit_sum % 10
        carry = (total_digit_sum - total_digit) // 10
        total_digit_list.insert(0, total_digit)
    return total_digit_list

def factorial(n:int) -> int:
    """
    Arguments:
        n: positive integer.
    Returns:
        Factorial of <n> = n*(n-1)*(n-2)*...*2*1.
    """
    factorial = 1
    for i in range(2, n+1):
        factorial *= i
    return factorial

def get_num_permutations(container:tp.Container[object]) -> int:
    """
    Arguments:
        container, of object.
    Returns:
        Number of unique permutations of <container>.
    """
    n = len(container)
    R = [len(list(group)) for key, group in it.groupby(sorted(container))]
    num_permutations = factorial(n)//prod(map(factorial, R))
    return num_permutations

def get_sum_proper_divisors(n:int) -> int:
    return sum(get_divisors(n=n)[:-1], 0)

def amicable_pairs(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    """
    > Yield pairs of amicable numbers.
    """
    idx = 1
    val = 2
    amicable_pairs = []
    exceeded_max = False
    while not exceeded_max:
        if idx>max_idx:
            exceeded_max = True
        elif val>max_val:
            exceeded_max = True
        elif not any(val==pair[1] for pair in amicable_pairs):
            other = get_sum_proper_divisors(n=val)
            if val!= other and val==get_sum_proper_divisors(n=other):
                idx += 1
                pair = (val, other)
                amicable_pairs.append(pair)
                yield pair
        val += 1

def fibonnaci_numbers(max_idx:int=math.inf, max_val:int=math.inf) -> tp.Generator:
    """
    > Yield Fibonacci numbers.
    """
    idx = 1
    prev = 1
    curr = 1
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
                val = curr+prev
                prev = curr
                curr = val
            if val>max_val:
                exceeded_max = True
            else:
                yield val
        idx += 1