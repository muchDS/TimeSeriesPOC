import numpy as np
import pandas as pd

from runge_kutta_integrator.integration_engine import RK4
from runge_kutta_integrator.integration_engine import Solver
from derivatives import rcast_deriv
from values_estimators import rcast_estimator


class RegimeEstimator(object):

    def __init__(
            self,
            input_values,
            df_dt=rcast_deriv,
            values_estimator=rcast_estimator,
            solver=Solver):
        self._set_input_values(input_values)
        self.df_dt = df_dt
        self.values_estimator = values_estimator
        self.solver = solver

    def _set_input_values(self, input_values):
        if isinstance(input_values, pd.Series):
            self.input_values = input_values
        else:
            raise ValueError(
                'Please provide one-dimensional pandas series')

