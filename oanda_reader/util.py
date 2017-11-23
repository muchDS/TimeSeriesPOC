import yaml


def read_creds(path=None):
    # read file
    info = _load_yaml('oanda_api.yaml', path)
    # return selected props
    return info['environment'], \
        info['account_id'], \
        info['token']


def which_fx_rates(path=None):
    # read file
    rates_yaml = _load_yaml('rates_to_read.yaml', path)
    return rates_yaml['fx']


def _get_path(fname, path=None):
    if path and fname not in path:
        full_path = '{}/{}'.format(path, fname)
    elif path and fname in path:
        full_path = path
    else:
        full_path = '{}'.format(fname)
    return full_path


def _load_yaml(fname, path=None):
    # create path string
    full_path = _get_path(fname, path)
    # read file
    with open(full_path, 'r') as yaml_file:
        return yaml.load(yaml_file)

