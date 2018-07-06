from heapq import nsmallest
from operator import itemgetter
import time

DEFAULT_SIZE = 1000
DEFAULT_MAX_AGE = 60 * 10

class Counter(dict):
    'Mapping where default values are zero'
    def __missing__(self, key):
        return 0

class CacheMiss(Exception):
    pass

#http://code.activestate.com/recipes/498245-lru-and-lfu-cache-decorators/
class Cache(object):
    def __init__(self, maxsize=DEFAULT_SIZE, state=None, ns=''):
        self._ = state or {}

        if not self._:
            self._['cache'] = {}
            self._['use_count'] = Counter()           # times each key has been accessed
            self._['hits'] = 0
            self._['miss'] = 0
            self._['maxsize'] = maxsize

        self._ns = ns
        self._sub_caches = {}

    def _purge(self):
        # purge least frequently used cache entry
        maxsize = self._['maxsize']
        use_count = self._['use_count']
        cache = self._['cache']

        if len(cache) >= maxsize:
            for key, _ in nsmallest(maxsize // 10,
                                    use_count.iteritems(),
                                    key=itemgetter(1)):
                del cache[key], use_count[key]

    def get(self, key, max_age=0, miss_exc=False):
        key = (self._ns, key)

        try:
            value, expiry = self._['cache'][key]
            t = time.time()
            if (expiry and expiry >= t and expiry >= t - max_age) or not expiry:
                self._['use_count'][key] += 1
                self._['hits'] += 1
                return value
        except KeyError:
            pass

        self._['miss'] += 1
        if miss_exc:
            raise CacheMiss
        return None

    def set(self, key, value, max_age=DEFAULT_MAX_AGE):
        key = (self._ns, key)

        self._purge()
        self._['use_count'][key] += 1

        expiry = time.time() + max_age if max_age else 0
        self._['cache'][key] = (value, expiry)

    def delete(self, key):
        key = (self._ns, key)

        try:
            del self._['cache'][key], self._['use_count'][key]
        except KeyError:
            pass

    def __getattr__(self, attr, default=False):
        if default:
            return self.__dict__[attr]

        sub_caches = self.__getattr__('_sub_caches', True)
        sub_ns = '%s.%s' % (self.__getattr__("_ns", True), attr)

        sub_cache = sub_caches.get(sub_ns, None)
        if sub_cache is not None:
            return sub_cache

        state = self.__getattr__('_', True)
        sub_cache = Cache(state=state, ns=sub_ns)
        sub_caches[sub_ns] = sub_cache

        return sub_cache

    def get_or_set(self, key, value, max_age=0):
        cached_value = self.get(key)
        if cached_value:
            return cached_value

        value = value() if callable(value) else value
        self.set(key, value, max_age)
        return value

if __name__ == '__main__':
    import pprint

    c = Cache(ns='cache')
    c.set('a', 5)
    c_a = c.a
    c_a.set('a', 5)
    c_a.set('b', 5)
    c_a_b = c_a.b
    c_a_b.set('a', 5)
    c_a_b.set('b', 5)

    pprint.pprint(c._['cache'])
