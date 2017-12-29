import numbers


def rcast_estimator(last_values, u, v_mtx):
    if isinstance(last_values, numbers.Number):
        estimate = u + v_mtx * last_values
    else:
        raise ValueError(
            'The values provided for integration are not of numeric type')
    return estimate
