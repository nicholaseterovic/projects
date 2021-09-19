
# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import typing as tp

####################################################################################################

def rgb_to_hex(rgb:tp.Tuple[int, int, int]) -> str:
    return "#{:x}{:x}{:x}".format(*rgb)

def hex_to_rgb(hex:str) -> tp.Tuple[int, int, int]:
    hex = hex.lstrip('#')
    N = len(hex)
    n = N//3
    rgb = tuple(int(hex[i:i+n], base=16) for i in range(0, N, n))
    return rgb