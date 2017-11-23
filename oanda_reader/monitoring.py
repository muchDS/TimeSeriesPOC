from readers import read_fx_rates


class DataReader(object):
    def __init__(self, frequency=10, duration=60, infinite=True):
        self.frequency = frequency
        self.duration = duration
        self.infinite = infinite

    def run_readers(self):
        read_fx_rates()
        pass
