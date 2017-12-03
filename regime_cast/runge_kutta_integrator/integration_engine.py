from datetime import datetime, timedelta
import numbers
import numpy as np
import pandas as pd
import time
import traceback


class Solver(object):
    def __init__(
            self, solving_algorithm, te):
        """
        Init with params. Time at which approximation starts and
        time increment are stored in solving_algorithm object.
        Time at which approximation ends should be provided.

        :param solving_algorithm: method of solving differential eq
        :param dim_names: names of forecast dimensions
        :param te: approximation end time
        :param t0: approximation start time
        :param dt: approximation time increment
        """
        self.solving_algorithm = solving_algorithm
        # fix time if type ambiguous
        if not isinstance(te, datetime):
            self.te = datetime.fromtimestamp(te)
        else:
            self.te = te
        # check if first step will fit into <t0: te>
        if(self.solving_algorithm.dt > te):
            raise RuntimeError(
                'Integration step is greater than the upper integration limit')
        self._spawn_storage()

    def _spawn_storage(self, dim_names='y'):
        """Spawning storage with given names"""
        _storage_dict = {}

        if not isinstance(dim_names, list):
            dim_names = [dim_names]

        for dim_name in dim_names:
            _storage_dict[dim_name] = []

        self.storage = pd.DataFrame(data=_storage_dict, index=[])

    def solve_eq(self):
        time = self.solving_algorithm.initial_time
        while time <= self.te:
            time, values = self.solving_algorithm.single_point_calcs()
            self.storage.loc[time] = values

    def get_storage(self):
        return self.storage


class EulersMethod(object):
    def __init__(
            self, initial_values, initial_time, df_dt, dt, dim_names='y'):
        """Initiate Euler's integration method"""
        # t0, y0 dt available here, number of iterations/end time not
        self.last_values = initial_values
        self.dim_names = dim_names
        self.set_proper_times(initial_time, dt)

        self.k1 = df_dt

    def set_proper_times(self, initial_time, dt):
        """Checks provided time formats, initializes calculation times
        and increments"""
        # check provided initial time and convert if needed
        if not isinstance(initial_time, datetime):
            self.initial_time = datetime.fromtimestamp(initial_time)
        else:
            self.initial_time = initial_time

        # set algorithms start time to 0
        self.last_time = 0

        # get proper time class if not provided
        if not isinstance(dt, timedelta):
            self.dt_dt = timedelta(seconds=dt)
            self.dt = dt
        else:
            self.dt_dt = dt
            self.dt.total_seconds()

    def single_point_calcs(self):
        # the approximating function
        # f(t1) = f(t0) + dt * df_dt(last_val, last_time)
        # if it's multivariate approximation other procedure should be used
        if isinstance(self.last_values, numbers.Number):
            self.last_values += self.dt * \
                               self.k1(self.last_values, self.last_time)
            self.last_time += self.dt
        else:
            pass

        # swap time to proper time (datetime + initial val)
        cur_time = self.initial_time + timedelta(seconds=self.last_time)
        # return calculated tuple
        return (cur_time, self.last_values)


class RK4(EulersMethod):
    def __init__(self):
        self.k1 = 0
        self.k2 = 0
        self.k3 = 0
        self.k4 = 0


if __name__ == '__main__':
    # initial_values, initial_time, df_dt, dt, dim_names='y'
    plain_euler = EulersMethod(
        initial_values=5,
        initial_time=time.time(),
        df_dt=lambda last_value, time: last_value,
        dt=0.1)
    simple_solver = Solver(plain_euler, time.time() + 160)
    simple_solver.solve_eq()
    print simple_solver.get_storage()
