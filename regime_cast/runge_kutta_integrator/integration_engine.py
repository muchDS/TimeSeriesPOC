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
        """Spawning storage with given variable names"""
        _storage_dict = {}

        if not isinstance(dim_names, list):
            dim_names = [dim_names]

        for dim_name in dim_names:
            _storage_dict[dim_name] = []

        self.storage = pd.DataFrame(data=_storage_dict, index=[])

    def solve_eq(self):
        values = self.solving_algorithm.initial_values
        real_time = init_time = self.solving_algorithm.initial_time
        last_time = 0
        while real_time <= self.te:
            last_time, values = \
                self.solving_algorithm\
                    .single_point_calcs(values, last_time,
                                        self.solving_algorithm.k1,
                                        self.solving_algorithm.dt,)
            real_time = init_time + timedelta(seconds=last_time)

            self.storage.loc[real_time] = values

    def get_storage(self):
        return self.storage


class EulersMethod(object):
    def __init__(
            self, initial_values, initial_time, df_dt, dt, dim_names='y'):
        """Initiate Euler's integration method"""
        # t0, y0 dt available here, number of iterations/end time not
        self.initial_values = initial_values
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

    @staticmethod
    def _return_desired_structure(last_time, last_values, vals_only=False):
        """
        Returns desired data structure (raw data or (timestamp, data)
        tuple for now)
        :param last_time: last timestamp value
        :param last_values: last value(s)
        :param vals_only: if only values should be returned
        :return: double or tuple for now
        """

        if isinstance(last_values, numbers.Number):
            if vals_only:
                return last_values
            else:
                return (last_time, last_values)
        else:
            raise ValueError(
                'The values provided for integration are not of numeric type')

    @staticmethod
    def single_point_calcs(
            last_values, last_time, k1, dt,
            dt_multiplier=1, df_dt=None, vals_only=False):
        # the approximating function
        # f(t1) = f(t0) + dt * df_dt(last_val, last_time)
        # if it's multivariate approximation other procedure should be used
        if df_dt:
            df_dt_used = df_dt
        else:
            df_dt_used = k1

        if isinstance(last_values, numbers.Number):
            last_values += dt_multiplier * dt * \
                               df_dt_used(last_values, last_time)
            last_time += dt_multiplier * dt
        else:
            pass

        # return calculated values or (time, values) tuple
        return EulersMethod._return_desired_structure(
            last_time, last_values, vals_only)
        # if vals_only:
        #     return last_values
        # else:
        #     return (last_time, last_values)


class RK4(EulersMethod):
    def __init__(self, initial_values, initial_time, df_dt, dt, dim_names='y'):
        super(RK4, self).\
            __init__(initial_values, initial_time, df_dt, dt, dim_names)
        # initializing k values
        self.k1 = self.k2 = self.k3 = self.k4 = df_dt
        # getting single point Euler integrator
        self._euler_single_point_calcs = EulersMethod.single_point_calcs

    def single_point_calcs(self,
                           last_values, last_time, k1, dt,
                           dt_multiplier=1, df_dt=None, vals_only=False):
        if df_dt:
            df_dt_used = df_dt
        else:
            df_dt_used = k1

        if isinstance(last_values, numbers.Number):
            # get k1 value
            k1_val = df_dt_used(last_values, last_time)
            # set the time for last_values_1 calcs
            last_time_1 = last_time + dt / 2
            # get the value at dt/2 y1
            last_values_1 = \
                self._euler_single_point_calcs(
                    last_values, last_time_1,
                    k1=df_dt_used,
                    dt=dt / 2,
                    vals_only=True)

            # get k2 = df_dt(dt/2, y1)
            k2_val = df_dt_used(last_values_1, last_time_1)
            # get value at dt/2 based on k2 y2
            # set time for last_values_2 calcs
            last_time_2 = last_time_1  # same as time for y_1
            last_values_2 = \
                self._euler_single_point_calcs(
                    last_values, last_time_2,
                    k1=df_dt_used,
                    dt=dt / 2,
                    vals_only=True)
            # get k3 = df_dt(dt/2, y2)
            k3_val = df_dt_used(last_values_2, last_time_2)
            # get value at dt based on k3 y3
            last_values_3 = \
                self._euler_single_point_calcs(
                    last_values, last_time,
                    k1=df_dt_used,
                    dt=dt,
                    vals_only=True
                )
            # get k4 = df_dt(dt/2, y3)
            k4_val = df_dt_used(last_values_3, last_time + dt)

            last_values += \
                dt * (k1_val +
                      2 * k2_val +
                      2 * k3_val +
                      k4_val) / 6
            last_time += dt
        else:
            raise ValueError(
                'The values provided for integration are not of numeric type')

        return EulersMethod._return_desired_structure(
            last_time, last_values, vals_only)

        # if vals_only:
        #     return last_values
        # else:
        #     return (last_time, last_values)


if __name__ == '__main__':
    # initial_values, initial_time, df_dt, dt, dim_names='y'
    plain_euler = EulersMethod(
        initial_values=5,
        initial_time=time.time(),
        df_dt=lambda last_value, time: -2*last_value,
        dt=0.1)

    rk_4 = RK4(
        initial_values=5,
        initial_time=time.time(),
        df_dt=lambda last_value, time: -2 * last_value,
        dt=0.1)

    simple_solver_euler = Solver(plain_euler, time.time() + 2)
    simple_solver_euler.solve_eq()
    print 'Euler'
    print simple_solver_euler.get_storage()

    rk_4_solver = Solver(rk_4, time.time() + 2)
    rk_4_solver.solve_eq()
    print 'RK4'
    print rk_4_solver.get_storage()
