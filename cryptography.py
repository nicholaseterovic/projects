# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source imports.
import abc
import typing as tp

####################################################################################################

class Cipher(abc.ABC):
    def __init__(self, key:object) -> object:
        self.key = key

    def encrypt(plaintext:str, *args:tp.Tuple[object], **kwargs:tp.Dict[object, object]) -> str:
        raise NotImplementedError

    def decrypt(ciphertext:str, *args:tp.Tuple[object], **kwargs:tp.Dict[object, object]) -> str:
        raise NotImplementedError

####################################################################################################