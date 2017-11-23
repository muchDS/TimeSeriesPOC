import numpy as np
import pandas as pd


class EulersMethod(object):
    def __init__(self, df_dt, t0, te, dt, y0):
        """Initiate Euler's integration method"""
        self.approximation_window = range(t0, te + dt, dt)
        self.k1 = 0
        # f(y(t), t)
        self.df_dt = df_dt()
        self.dt = dt
        self._set_init_values(self, y0, t0)

    def _set_init_values(self, y0, t0):
        """Set initial values"""
        #
        self.last_time = t0
        self.last_df_dt = self.df_dt(y0, t0 + self.dt)
        self.last_value = y0

    def _spawn_storage(self, dim_names, time_series = True):
        """Spawning storage with given names"""
        _storage_dict = {}

        for dim_name in dim_names:
            _storage_dict[dim_name] = []

        if time_series == True:
            self.storage = pd.Series(data=_storage_dict, index=[])
        else :
            self.storage = pd.DataFrame(data=_storage_dict, index=[])

    def single_piont_calcs(self):
        # the approximating function
        # f(t1) = f(t0) + dt * df_dt(last_val, last_time)
        self.last_value += self.dt * \
                           self.df_dt(self.last_value, self.last_time)
        self.last_time += self.dt


    def solve_eq(self):
        for t in self.approximation_window:



class RK4(EulersMethod):
    def __init__(self):
        self.k1 = 0
        self.k2 = 0
        self.k3 = 0
        self.k4 = 0
