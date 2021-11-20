# Nicholas Eterovic 2020Q4
####################################################################################################

# Open-source packages.
import sys

####################################################################################################

def get_cli_kwargs() -> dict:
    kwargs = dict([
        arg.lstrip("-").split(sep="=", maxsplit=1)
        for arg in sys.argv[1:] if arg.startswith("-") and "=" in arg    
    ])
    for kw, arg in kwargs.items():
        if arg in ["True", "False", "None"]:
            kwargs[kw] = eval(arg)
    return kwargs