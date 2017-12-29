import numbers


def rcast_deriv(last_time, last_values, p, q_mtx, a_mtx):
    if isinstance(last_values, numbers.Number):
        deriv_val = p + q_mtx * last_values + a_mtx * last_values
    else:
        raise ValueError(
            'The values provided for integration are not of numeric type')

    return deriv_val
