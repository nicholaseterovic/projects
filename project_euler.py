# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import math
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

def get_divisors(n:int) -> tp.List[int]:
    prime_decomposition = get_prime_decomposition(n=n)
    divisors = {1, n}
    for r in range(1, len(prime_decomposition)):
        for primes in set(it.combinations(prime_decomposition, r=r)):
            divisor = prod(primes, default=1)
            divisors.add(divisor)
    return sorted(divisors)
    
def solution_012(min_num_divisors:int=500) -> int:
    for triangle_number in triangle_numbers():
        divisors = get_divisors(triangle_number)
        num_divisors = len(divisors)
        if num_divisors>min_num_divisors:
            return triangle_number

####################################################################################################

def sum_digit_lists(digit_lists:tp.List[tp.List[int]]) -> tp.List[int]:
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
    
def solution_013(num_first_digits:int=10) -> int:
    numbers_str = """
    37107287533902102798797998220837590246510135740250
    46376937677490009712648124896970078050417018260538
    74324986199524741059474233309513058123726617309629
    91942213363574161572522430563301811072406154908250
    23067588207539346171171980310421047513778063246676
    89261670696623633820136378418383684178734361726757
    28112879812849979408065481931592621691275889832738
    44274228917432520321923589422876796487670272189318
    47451445736001306439091167216856844588711603153276
    70386486105843025439939619828917593665686757934951
    62176457141856560629502157223196586755079324193331
    64906352462741904929101432445813822663347944758178
    92575867718337217661963751590579239728245598838407
    58203565325359399008402633568948830189458628227828
    80181199384826282014278194139940567587151170094390
    35398664372827112653829987240784473053190104293586
    86515506006295864861532075273371959191420517255829
    71693888707715466499115593487603532921714970056938
    54370070576826684624621495650076471787294438377604
    53282654108756828443191190634694037855217779295145
    36123272525000296071075082563815656710885258350721
    45876576172410976447339110607218265236877223636045
    17423706905851860660448207621209813287860733969412
    81142660418086830619328460811191061556940512689692
    51934325451728388641918047049293215058642563049483
    62467221648435076201727918039944693004732956340691
    15732444386908125794514089057706229429197107928209
    55037687525678773091862540744969844508330393682126
    18336384825330154686196124348767681297534375946515
    80386287592878490201521685554828717201219257766954
    78182833757993103614740356856449095527097864797581
    16726320100436897842553539920931837441497806860984
    48403098129077791799088218795327364475675590848030
    87086987551392711854517078544161852424320693150332
    59959406895756536782107074926966537676326235447210
    69793950679652694742597709739166693763042633987085
    41052684708299085211399427365734116182760315001271
    65378607361501080857009149939512557028198746004375
    35829035317434717326932123578154982629742552737307
    94953759765105305946966067683156574377167401875275
    88902802571733229619176668713819931811048770190271
    25267680276078003013678680992525463401061632866526
    36270218540497705585629946580636237993140746255962
    24074486908231174977792365466257246923322810917141
    91430288197103288597806669760892938638285025333403
    34413065578016127815921815005561868836468420090470
    23053081172816430487623791969842487255036638784583
    11487696932154902810424020138335124462181441773470
    63783299490636259666498587618221225225512486764533
    67720186971698544312419572409913959008952310058822
    95548255300263520781532296796249481641953868218774
    76085327132285723110424803456124867697064507995236
    37774242535411291684276865538926205024910326572967
    23701913275725675285653248258265463092207058596522
    29798860272258331913126375147341994889534765745501
    18495701454879288984856827726077713721403798879715
    38298203783031473527721580348144513491373226651381
    34829543829199918180278916522431027392251122869539
    40957953066405232632538044100059654939159879593635
    29746152185502371307642255121183693803580388584903
    41698116222072977186158236678424689157993532961922
    62467957194401269043877107275048102390895523597457
    23189706772547915061505504953922979530901129967519
    86188088225875314529584099251203829009407770775672
    11306739708304724483816533873502340845647058077308
    82959174767140363198008187129011875491310547126581
    97623331044818386269515456334926366572897563400500
    42846280183517070527831839425882145521227251250327
    55121603546981200581762165212827652751691296897789
    32238195734329339946437501907836945765883352399886
    75506164965184775180738168837861091527357929701337
    62177842752192623401942399639168044983993173312731
    32924185707147349566916674687634660915035914677504
    99518671430235219628894890102423325116913619626622
    73267460800591547471830798392868535206946944540724
    76841822524674417161514036427982273348055556214818
    97142617910342598647204516893989422179826088076852
    87783646182799346313767754307809363333018982642090
    10848802521674670883215120185883543223812876952786
    71329612474782464538636993009049310363619763878039
    62184073572399794223406235393808339651327408011116
    66627891981488087797941876876144230030984490851411
    60661826293682836764744779239180335110989069790714
    85786944089552990653640447425576083659976645795096
    66024396409905389607120198219976047599490197230297
    64913982680032973156037120041377903785566085089252
    16730939319872750275468906903707539413042652315011
    94809377245048795150954100921645863754710598436791
    78639167021187492431995700641917969777599028300699
    15368713711936614952811305876380278410754449733078
    40789923115535562561142322423255033685442488917353
    44889911501440648020369068063960672322193204149535
    41503128880339536053299340368006977710650566631954
    81234880673210146739058568557934581403627822703280
    82616570773948327592232845941706525094512325230608
    22918802058777319719839450180888072429661980811197
    77158542502016545090413245809786882778948721859617
    72107838435069186155435662884062257473692284509516
    20849603980134001723930671666823555245252804609722
    53503534226472524250874054075591789781264330331690
    """
    digit_lists = [
        [int(digit_str) for digit_str in number_str]
        for number_str in numbers_str.strip().split()
    ]
    total_digit_list = sum_digit_lists(digit_lists=digit_lists)
    first_digits = total_digit_list[:num_first_digits]
    return sum(digit*10**i for i, digit in enumerate(reversed(first_digits)))

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

def factorial(n:int) -> int:
    factorial = 1
    for i in range(2, n+1):
        factorial *= i
    return factorial

def get_num_permutations(container:tp.Container) -> int:
    n = len(container)
    R = [len(list(group)) for key, group in it.groupby(sorted(container))]
    num_permutations = factorial(n)//prod(map(factorial, R))
    return num_permutations
    
def solution_015(grid_length:int=20) -> int:
    moves = grid_length*['DOWN', 'RIGHT']
    return get_num_permutations(moves)

####################################################################################################

def solution_016(n:int=2**1000) -> int:
    return sum(map(int, str(n)), 0)

####################################################################################################

def is_leap_year(YYYY:int) -> bool:
    if YYYY % 100 == 0:
        if YYYY % 400 == 0:
            return True
        return False
    if YYYY % 4 == 0:
        return True
    return False

def get_num_days_in_month(YYYY:int, MM:int) -> int:
    if MM==2:
        if is_leap_year(YYYY):
            return 29
        return 28
    if MM in [4, 6, 9, 11]:
        return 30
    return 31

def parse_date(YYYYMMDD:int) -> tp.Tuple[int, int, int]:
    DD = YYYYMMDD % 100
    MM = ((YYYYMMDD-DD) % 10000) // 100
    YYYY = (YYYYMMDD-100*MM-DD) // 10000
    return (YYYY, MM, DD)
    
def get_dates_between(sYYYYMMDD:int, eYYYYMMDD:int) -> tp.List[int]:
    sYYYY, sMM, sDD = parse_date(YYYYMMDD=sYYYYMMDD)
    eYYYY, eMM, eDD = parse_date(YYYYMMDD=eYYYYMMDD)
    return [
        10000*YYYY+100*MM+DD
        for YYYY in range(
            sYYYY,
            eYYYY+1,
        )
        for MM in range(
            sMM if YYYY==sYYYY else 1,
            (eMM if YYYY==eYYYY else 12)+1,
        )
        for DD in range(
            sDD if YYYY==sYYYY and MM==sMM else 1,
            (eDD if YYYY==eYYYY and MM==eMM else get_num_days_in_month(YYYY, MM))+1,
        )
    ]

def solution_019(sYYYYMMDD:int=19010101, eYYYYMMDD:int=20001231, day_of_week:int=7) -> int:
    date_mon = 19000101
    dates = get_dates_between(min(date_mon, sYYYYMMDD), max(date_mon, eYYYYMMDD))
    i_mon = dates.index(date_mon)
    i_dow = i_mon+day_of_week-1
    return len([
        date
        for date in dates[i_dow%7::7]
        if sYYYYMMDD<=date<=eYYYYMMDD and parse_date(date)[2]==1
    ])

####################################################################################################

def solution_020(n:int=100) -> int:
    return sum(int(digit) for digit in str(factorial(n=n)))

####################################################################################################

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

def solution_021(n:int=1e4) -> int:
    return sum(n for pair in amicable_pairs(max_val=n) for n in pair)