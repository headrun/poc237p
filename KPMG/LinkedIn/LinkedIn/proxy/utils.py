from socket import *
import time

try:
    from django.conf import settings
except ImportError:
    settings = None

class Counter:

    def _get_from_settings(self, key, default=None):
        try:
            return getattr(settings, key, default)
        except ImportError:
            return default

    def __init__(self, flush_num_seconds=None,
        flush_num_updates=None,
        flush_num_keys=None):

        G = self._get_from_settings
        self.flush_num_seconds = flush_num_seconds or G('COUNTERS_FLUSH_NUM_SECONDS', 10)
        self.flush_num_keys = flush_num_keys or G('COUNTERS_FLUSH_NUM_KEYS', 100000)
        self.flush_num_updates = flush_num_updates or G('COUNTERS_FLUSH_NUM_UPDATES', 10000)
        self._last_flushed_at = time.time()
        self._num_updates = 0
        self.counters = {}
        self.statsd = Statsd()

    def _increment(self, keys):
        _keys = []

        for k, increment in keys.iteritems():
            count = self.counters.setdefault(k, 0)
            self.counters[k] = count + increment

        return _keys

    def _update(self, keys):
        _keys = []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]

        for k in keys:
            count = self.counters.setdefault(k, 0)
            self.counters[k] = count + 1

        return _keys

    def update(self, keys, dt=None, epoch=None):
        self._num_updates += 1

        if isinstance(keys, dict):
            _keys = self._increment(keys)
        else:
            _keys = self._update(keys)

        self._check_and_flush()
        return _keys

    def _check_and_flush(self):
        if (get_current_timestamp() - self._last_flushed_at) > self.flush_num_seconds:
            self.flush()

        if self._num_updates > self.flush_num_updates:
            self.flush()
            self._num_updates = 0

        if len(self.counters) > self.flush_num_keys:
            self.flush()

    def flush(self):
        self._last_flushed_at = time.time()

        if not self.statsd or not self.counters:
            return

        lines = []
        for key, value in self.counters.iteritems():
            self.statsd.update_stats(key, value)

        self.counters = {}

class Statsd():

    def _get_from_settings(self, key, default=None):
        try:
            return getattr(settings, key, default)
        except ImportError:
            return default

    def __init__(self):
        G = self._get_from_settings
        self.host = G('STATSD_SERVER', 'localhost')
        self.port = G('STATSD_PORT', 8125)

    def _update_stats(self, key, value):
        data = "%s:%s|c" % (key, value)
        udp_sock = socket(AF_INET, SOCK_DGRAM)
        udp_sock.sendto(data, (self.host, self.port))

    def update_stats(self, key, value=1):
        if isinstance(key, (str, unicode)):
            self._update_stats(key, value)
        else:
            stats = key
            for item in stats:
                if isinstance(item, (str, unicode)):
                    self._update_stats(item, value)

                else:
                    key, value = item
                    self._update_stats(P + key, value)

