__docformat__ = 'restructuredtext en'
__author__ = 'eflee'

import zope.interface
import ipaddress
import sources
import collections
import time
import random
import requests


class IIPProvider(zope.interface.Interface):
    def add_source(self, source):
        """Adds a source to the set being used by the provider"""

    def get_ip(self):
        """Round robin through the configured providers until one returns an IP, then cache it"""

    def get_info(self, required_info_keys=None):
        """Round robin through the configured providers until one returns the keys required, then cache it"""

    def invalidate_cache(self):
        """Invalidates the cache"""

    def is_cache_valid(self):
        """Evaluates the validity of the cache"""


class IPProvider(object):
    zope.interface.implements(IIPProvider)

    def __init__(self, source_list=None, cache_ttl=3600):
        """
        The IPProvider takes one or more IPSources and returns the results from them . If one
        provider does not respond it will move on to the next. It ensures that the age of the
        response on no older than the cache_ttl.

        :param source_list: The list of sources to bootstrap the provider with
        :type source_list: list of IIPSource providers
        :param cache_ttl: the seconds the ip cache remains valid
        :type cache_ttl: int
        """
        self._sources = collections.defaultdict(dict)

        if source_list:
            for source in source_list:
                self.add_source(source)

        self._cache_ttl = cache_ttl

        self._cache_ip = None
        self._cache_info = None
        self._cache_timestamp = 0

    def add_source(self, source):
        """
        Adds a source to the set being used by the provider
        :param source: The IIPSource provider to add to sources
        :type source: IIPSource provider
        """
        if sources.IIPSource.providedBy(source):
            self._sources[source]['fail_count'] = 0
        else:
            raise TypeError('gimmeip.sources.IIPSource must be provided by source argument.')

    def get_ip(self):
        """
        Round robin through the configured providers until one returns an IP, then cache it
        :return: the current ip
        :rtype: ipaddress.IPv4Address or ipaddress.IPv6Address
        """
        if not self.is_cache_valid() or self._cache_ip is None:
            self._cache_ip, self._cache_info = self._fetch_from_sources()
            self._cache_timestamp = time.time()
        return self._cache_ip

    def get_info(self, required_info_keys=None):
        """
        Round robin through the configured providers until one returns the keys required, then cache it
        :param required_info_keys: The keys required for the fetch to be valid
        :type required_info_keys: list(tuple)
        :return: The info dictionary returned by the provider
        :rtype: dict
        """
        if not self.is_cache_valid or not self._cache_info or not self._verify_required_keys(required_info_keys):
            self._cache_ip, self._cache_info = self._fetch_from_sources(required_info_keys)
            self._cache_timestamp = time.time()
        return self._cache_info

    def _fetch_from_sources(self, required_info_keys=None):
        sources = self._sources.keys()
        random.shuffle(sources)
        for source in sources:
            try:
                source.refresh()

                ip = source.ip
                info = source.info

                if not required_info_keys or self._verify_required_keys(info, required_info_keys):
                    return ip, info

            except (ValueError, requests.ConnectionError) as e:
                print e
                continue

        return None, None

    @staticmethod
    def _verify_required_keys(info, required_info_keys):
        keys_found = True
        for key in required_info_keys:
            if isinstance(key, (tuple, list)):
                if not any([subkey in info for subkey in key]):
                    keys_found = False
                    break
            else:
                if key not in info:
                    keys_found = False
                    break
        return keys_found

    def invalidate_cache(self):
        """
        Invalidates the cache
        """
        self._cache_timestamp = 0

    def is_cache_valid(self):
        """
        Evaluates the validity of the cache
        """
        return time.time() - self._cache_timestamp < self._cache_ttl \
            and self._cache_info is not None and self._cache_ip is not None

    @property
    def num_sources(self):
        return len(self._sources)