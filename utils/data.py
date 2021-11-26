
# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source packages.
import typing as tp

####################################################################################################

def flatten_dict(d:dict, label:str="id", children:str="children") -> tp.List[dict]:
    flattened = []
    for child in d.get(children, []):
        flattened.append({"parent":d[label], label:child[label], **child})
        flattened_child = flatten_dict(d=child, label=label, children=children)
        flattened.extend(flattened_child)
    return flattened