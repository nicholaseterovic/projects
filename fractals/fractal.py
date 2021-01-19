# Nicholas Eterovic 2020Q4

####################################################################################################

# Open-source packages.
import numpy as np
import typing as tp
import pandas as pd
import itertools as it
import plotly.offline as py

class Fractal:
    
    def __init__(self:object, seed:tp.List[tuple], generator:tp.List[tuple]) -> object:
        self.seed = seed
        self.generator = generator

        self._seed = pd.DataFrame(dict(enumerate(zip(*self.seed))))
        self._generator = pd.DataFrame(dict(enumerate(zip(*self.generator))))
        self._iterations = {}

    @staticmethod
    def _get_rotation_matrix(rads:float=np.pi/2) -> pd.DataFrame:
        cos, sin = np.cos(rads), np.sin(rads)
        rotation_matrix = pd.DataFrame([[+cos, -sin], [+sin, +cos]])
        return rotation_matrix
    
    @staticmethod
    def _interpolate(start:pd.Series, end:pd.Series, generator:pd.DataFrame) -> pd.DataFrame:
        
        u_vec = generator.iloc[-1] - generator.iloc[0]
        v_vec = end - start

        u_len = u_vec.pow(2).sum()**.5
        v_len = v_vec.pow(2).sum()**.5

        scale = v_len/u_len
        angle = np.arccos((u_vec*v_vec).sum()/(u_len*v_len))
        if u_vec[0]*v_vec[1]-u_vec[1]*v_vec[0] > 0:
            angle *= -1

        rotation = Fractal._get_rotation_matrix(angle)
        interpolation = generator.sub(generator.iloc[0]).mul(scale).dot(rotation).add(start)
        return interpolation
    
    def get_iteration(self:object, n:int=0) -> pd.DataFrame:
        if not isinstance(n, int) or n<0:
            raise ValueError(n)
        elif n==0:
            return self._seed
        elif n in self._iterations:
            return self._iterations[n]
        else:
            prev_iteration = self.get_iteration(n=n-1)
            iteration = pd.concat(ignore_index=True, objs=[
                Fractal._interpolate(
                    start=prev_iteration.iloc[i],
                    end=prev_iteration.iloc[i+1],
                    generator=self._generator,
                ).iloc[int(i>0):]
                for i in range(len(prev_iteration)-1)
            ])
            self._iterations[n] = iteration
            return iteration