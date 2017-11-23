import multiprocessing as mp
import oandapy
import traceback
import time
from util import read_creds, which_fx_rates


class Reader(object):
    def __init__(self, poller=None, *args, **kwargs):
        if poller:
            self.poller = poller
        self.args = args
        self.kwargs = kwargs

    def spawn(self):
        self.monit_proc = \
            mp.Process(target=self.poller) #, args=self.args, kwargs=self.kwargs)

    def start(self):
        try:
            self.monit_proc.start()
        except Exception as exc:
            print exc
            traceback.print_exc()

    def stop(self):
        try:
            self.monit_proc.terminate()
            self.monit_proc.join()
        except Exception as exc:
            print exc
            traceback.print_exc()


class OandaReader(Reader):
    def __init__(self):
        super(OandaReader, self).__init__()
        self.poller = self.read_rates
        self.environment, self.account_id, self.token = \
            read_creds()
        self.fx_rates = which_fx_rates()

    def get_session(self):
        self.oanda = oandapy.API(
            environment=self.environment,
            access_token=self.token)

    def read_rates(self):
        self.get_session()
        fx_json = self.oanda.get_prices(instruments=self.fx_rates)
        rates = fx_json.get('prices')
        # publish rates to kafka
        self.publish_rates()
        print rates

    def publish_rates(self):
        pass


class Monitoring(object):
    def __init__(self, fx_reader_obj):
        self.monitors = []
        self.monitors.append(fx_reader_obj)

    def _init_monitors(self):
        for monitor in self.monitors:
            monitor.spawn()

    def start_all_monits(self):
        for monitor in self.monitors:
            print monitor.monit_proc
            monitor.start()

    def stop_all_monits(self):
        for monitor in self.monitors:
            monitor.stop()

    def start_monitoring(self, duration=300, freq=5):
        start_time = time.time()
        iter_count = 0

        while(time.time() < start_time + duration):
            iter_count += 1
            self._init_monitors()
            self.start_all_monits()
            time_after_start = time.time()
            wait_time = \
                (start_time + freq * iter_count - time_after_start)
            time.sleep(wait_time)
            self.stop_all_monits()
            # idle_time = \
            #     start_time + iter_count * freq - time.time()
            # time.sleep(idle_time)


if __name__ == '__main__':
    q = Monitoring(fx_reader_obj=OandaReader())
    q.start_monitoring()
