# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source imports.
import abc
import string
import typing as tp

####################################################################################################

class Cipher(abc.ABC):

    def encrypt(self, plaintext:str, *args:tp.Tuple[object], **kwargs:tp.Dict[object, object]) -> str:
        raise NotImplementedError

    def decrypt(self, ciphertext:str, *args:tp.Tuple[object], **kwargs:tp.Dict[object, object]) -> str:
        raise NotImplementedError

class CryptAnalyzer(abc.ABC):

    def crack(self, ciphertext:str, *args:tp.Tuple[object], **kwargs:tp.Dict[object, object]) -> str:
        raise NotImplementedError

####################################################################################################

class SubstitutionCipher(Cipher):
    def __init__(self, char_map:tp.List[tp.Tuple[str, str]]) -> object:
        self.char_map = char_map

    @classmethod
    def from_keyphrase(cls, keyphrase:str) -> object:
        chars_from = string.ascii_lowercase
        chars_to = []
        for char in filter(None, keyphrase):
            if char not in chars_to:
                chars_to.append(char)
        # TODO: add remaining chars to cipher alphabet.
        char_map = list(zip(chars_from, chars_to))
        return cls(char_map=char_map)


    def encrypt(self, plaintext:str) -> str:
        char_map = {char_from:char_to for char_from, char_to in self.char_map}
        ciphertext = ''.join(char_map.get(char, char) for char in plaintext)
        return ciphertext

    def decrypt(self, ciphertext:str) -> str:
        char_map = {char_from:char_to for char_to, char_from in self.char_map}
        plaintext = ''.join(char_map.get(char, char) for char in ciphertext)
        return plaintext

class CaeserCipher(SubstitutionCipher):
    def __init__(self, shift:int=0) -> object:
        self.shift = shift
        shift = shift % 26
        chars_from = string.ascii_lowercase
        chars_to = chars_from[self._shift:] + chars_from[:self._shift]
        char_map = list(zip(chars_from, chars_to))
        super().__init__(char_map=char_map)