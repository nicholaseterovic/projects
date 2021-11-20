# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import sys
import json
import math
import inspect
import num2words 
import typing as tp
import functools as ft
import itertools as it
import pyinstrument as pi
import more_itertools as mit

# In-house packages.
import utils.sets as su
import utils.numbers as nu
import utils.temporal as tu
from utils.tree import Node
from utils.collatz import CollatzTree

####################################################################################################

def solution_001(n:int=1000, K:tp.List[int]=[3, 5], agg=sum) -> int:
    sets = [set(range(k, n, k)) for k in K]
    solution = su.get_agg_union_sets(sets=sets, agg=agg)
    return solution

def solution_002(max_val:int=4e6) -> int:
    return sum(nu.even_fibonnaci_numbers(max_val=max_val), 0)

def solution_003(n:int=600851475143) -> int:
    return max(nu.get_prime_decomposition(n=n))

def solution_004(numbers:int=2, digits:int=3) -> int:
    rng = range(int("9"*digits), int("1"*digits)-1, -1)
    nums = it.product(rng, repeat=numbers)
    max_palindrome = -math.inf
    for num in nums:
        if any(n<m for n, m in zip(num[:-1], num[1:])):
            continue
        val = nu.prod(num)
        val_str = str(val)
        if val_str==val_str[::-1] and val>max_palindrome:
            max_palindrome = val
    return max_palindrome

def solution_005(n:int=20) -> int:
    return nu.get_lcm(*range(1, n+1))

def solution_006(n:int=100) -> int:
    sum_of_squares = nu.get_sum_of_powers(n=n, power=2)
    square_of_sum = nu.get_sum_of_powers(n=n, power=1)**2
    return abs(sum_of_squares-square_of_sum)

def solution_007(i:int=10001) -> int:
    for prime in nu.primes(max_idx=i):
        pass
    return prime

def solution_008(n:int=13, file:str="data/project_euler/p008_number.txt") -> int:
    with open(file=file, mode="r") as file_handle:
        num_str = file_handle.read()
    num_str = "".join(num_str.split())
    num_list = [int(num) for num in num_str]
    num_sublists = [num_list[i:i+n] for i in range(0, len(num_list)+1-n)]
    max_prod = -math.inf
    for num_sublist in num_sublists:
        if max_prod>-math.inf and 0 in num_sublist:
            continue
        num_subiter = filter(int(1).__ne__, num_sublist)
        prod_num = nu.prod(num_subiter, default=1)
        if prod_num>max_prod:
            max_prod = prod_num
    return max_prod

def solution_009(perimeter:int=1000) -> int:
    pythag_triples = nu.get_pythag_triples(perimeter=perimeter)
    a, b, c = max(pythag_triples)
    return a*b*c

def solution_010(n:int=2e6) -> int:
    return sum(nu.primes(max_val=n))

def solution_011(adj_num:int=4, file:str="data/project_euler/p011_matrix.txt") -> int:
    with open(file=file, mode="r") as file_handle:
        matrix_str = file_handle.read()
    matrix = [
        [int(num_str) for num_str in row_str.strip().split(" ")]
        for row_str in matrix_str.strip().split("\n")
    ]
    return nu.get_max_adj_prod(matrix=matrix, adj_num=adj_num)
    
def solution_012(min_num_divisors:int=500) -> int:
    for triangle_number in nu.triangle_numbers():
        divisors = nu.get_divisors(triangle_number)
        num_divisors = len(divisors)
        if num_divisors>min_num_divisors:
            return triangle_number
    
def solution_013(num_first_digits:int=10, file:str="data/project_euler/p013_numbers.txt") -> int:
    with open(file=file, mode="r") as file_handle:
        numbers_str = file_handle.read()
    digit_lists = [
        [int(digit_str) for digit_str in number_str]
        for number_str in numbers_str.strip().split()
    ]
    total_digit_list = nu.sum_digit_lists(digit_lists=digit_lists)
    first_digits = total_digit_list[:num_first_digits]
    return sum(digit*10**i for i, digit in enumerate(reversed(first_digits)))

def solution_014(max_num:int=1e6) -> int:
    nums = range(1, int(max_num))
    collatz_tree = CollatzTree()
    return max(nums, key=collatz_tree.get_length)
    
def solution_015(grid_length:int=20) -> int:
    moves = grid_length*["DOWN", "RIGHT"]
    return nu.get_num_permutations(moves)

def solution_016(n:int=2**1000) -> int:
    return sum(map(int, str(n)), 0)

def solution_017(n:int=1000) -> int:
    nums = range(1, n+1)
    num2chars = lambda num:num2words.num2words(num).replace("-", "").replace(" ", "")
    num_chars = map(num2chars, nums)
    num_char_counts = map(len, num_chars)
    num_char_count = sum(num_char_counts)
    return num_char_count

def solution_018(file:str="data/project_euler/p018_triangle.txt") -> int:
    with open(file=file, mode="r") as file_handle:
        triangle_str = file_handle.read()
    triangle_matrix = [
        [int(num_str) for num_str in row_str.split()]
        for row_str in triangle_str.strip().split("\n")
    ]
    node = Node.from_triangle_matrix(triangle_matrix=triangle_matrix)
    return sum(node.maximal_path)

def solution_019(sYYYYMMDD:int=19010101, eYYYYMMDD:int=20001231, day_of_week:int=7) -> int:
    date_mon = 19000101
    dates = tu.get_dates_between(min(date_mon, sYYYYMMDD), max(date_mon, eYYYYMMDD))
    i_mon = dates.index(date_mon)
    i_dow = i_mon+day_of_week-1
    return len([
        date
        for date in dates[i_dow%7::7]
        if sYYYYMMDD<=date<=eYYYYMMDD and tu.parse_date(date)[2]==1
    ])

def solution_020(n:int=100) -> int:
    return sum(int(digit) for digit in str(nu.factorial(n=n)))

def solution_021(n:int=1e4) -> int:
    return sum(n for pair in nu.amicable_pairs(max_val=n) for n in pair)

def solution_023(n:int=28123) -> int:
    abundant_numbers = filter(lambda x:x<nu.get_sum_proper_divisors(x), range(1, 1+n))
    abundant_pairs = it.combinations_with_replacement(iterable=abundant_numbers, r=2)
    abundant_pair_sums = set(map(sum, abundant_pairs))
    return sum(i for i in range(1, n+1) if i not in abundant_pair_sums)

def solution_022(file:str="data/project_euler/p022_names.txt") -> int:
    with open(file=file, mode="r") as file_handle:
        text = file_handle.read()
    names = sorted(text.replace("'", "").split(","))
    offset = ord("A")-1
    scores = (i*(sum(map(ord, name))-len(name)*offset) for i, name in enumerate(names, 1))
    return sum(scores)

def solution_024(digits_str:str="0123456789", i:int=1000000) -> str:
    perms = map("".join, it.permutations(iterable=digits_str, r=len(digits_str)))
    lex_perms = sorted(perms)
    lex_perm = lex_perms[i-1]
    return lex_perm

def solution_025(min_num_digits:int=1000) -> int:
    i = 0
    fib_nums = nu.fibonnaci_numbers()
    num_digits = -math.inf
    while num_digits<min_num_digits:
        fib_num = next(fib_nums)
        num_digits = len(str(fib_num))
        i += 1
    return i

def solution_028(spiral_dim:int=1001) -> int:
    return 1+sum(16*n**2+4*n+4 for n in range(1+(spiral_dim-1)//2))

def solution_029(a_max:int=100, b_max:int=100) -> int:
    B = range(2, 1+b_max)
    A = map(nu.get_prime_decomposition, range(2, 1+a_max))
    ApB = (sorted(a*b) for a, b in it.product(A, B))
    return len(set(map(tuple, ApB)))

def solution_035(n:int=1e6) -> int:
    return

def solution_067(file:str="data/project_euler/p067_triangle.txt") -> int:
    return solution_018(file=file)

####################################################################################################
# LAYOUT

# Dash packages.
import dash
import dash_ace as dac
from dash import dcc
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_bootstrap_components as dbc

app_layout = [
    dbc.Row(className="g-0", children=[
        dbc.Col(width=6, children=[
            dbc.Card([
                dbc.CardHeader([
                    "Problem",
                ]),
                dbc.CardBody([
                    
                ]),
            ]),
        ]),
        dbc.Col(width=6, children=[
            dbc.Card([
                dbc.CardHeader([
                    "Solution",
                ]),
                dbc.CardBody([
                    dac.DashAceEditor(
                        id="editor-euler-solution",
                        placeholder="Select a problem to view solution",
                        mode="python",
                        theme="monokai",
                    ),
                ]),
            ]),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size="sm",
                children=[
                    dbc.InputGroupText(
                        children="Solution:",
                    ),
                    dbc.Select(
                        id="select-solution-number",
                        value=None,
                        options=[
                            {"label":name.rsplit(sep="_", maxsplit=1)[-1], "value":name}
                            for name, obj in inspect.getmembers(
                                object=sys.modules[__name__],
                                predicate=inspect.isfunction,
                            )
                        ],
                    ),
                    dbc.Button(
                        id="button-solution-profile",
                        children="Profile",
                        n_clicks=0,
                        color="primary",
                    ),
                ],
            ),
        ]),
        dcc.Store(
            id="store-solution-profile",
            data={},
        ),
        dbc.CardBody([
            dcc.Graph(
                id="graph-solution-profile",
                figure={},
            ),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        ddp.Output("store-solution-profile", "data"),
        [ddp.Input("button-solution-profile", "n_clicks")],
        [ddp.State("select-solution-number", "value")],
    )
    def profile_solution(n_clicks:int, name:str) -> int:
        if not name:
            return {}
        func = getattr(sys.modules[__name__], name)

        print(inspect.getsource(func))
        with pi.Profiler() as profiler:
            func()
        profile_str = profiler.output(renderer=pi.renderers.JSONRenderer(show_all=False))
        profile_dict = json.loads(s=profile_str)
        return profile_dict

    @app.callback(
        ddp.Output("graph-solution-profile", "figure"),
        [ddp.Input("store-solution-profile", "data")],
    )
    def visualize_profile(data:dict) -> int:
        if not data:
            return {}
        
        root_frame = data.pop("root_frame")
        return {}