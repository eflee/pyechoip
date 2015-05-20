"""
Providers are objects that provide IPs from IPSources with caching
and (for MultisourceIPProvider) with consensus protocols.
"""
__docformat__ = 'restructuredtext en'
__author__ = 'Eli Flesher <eli@eflee.us>'

import collections
import time
import random

import zope.interface

import requests

from . import sources

# noinspection PyMethodMayBeStatic
class _IIPProvider(zope.interface.Interface):
    """
    Provider (zopes) interface specifying what public methods
    must be provided by a Provider
    """
    def __init__(self):
        """ Constructor """

    def add_source(self, source):
        """Adds a source to the set being used by the provider"""

    def get_ip(self):
        """
        Round robin through the configured providers until
        one returns an IP, then cache it.
        """

    def get_info(self, required_info_keys=None):
        """
        Round robin through the configured providers until
        one returns the keys required, then cache it.
        """

    def invalidate_cache(self):
        """Invalidates the cache"""

    def is_cache_valid(self):
        """Evaluates the validity of the cache"""


class IPProvider(object):
    """
    The IPProvider takes one or more IPSources and returns the results from them. If one
    provider does not respond it will move on to the next. It ensures that the age of the
    response on no older than the cache_ttl.
    """
    zope.interface.implements(_IIPProvider)

    def __init__(self, source_list=None, cache_ttl=3600):
        """
        Constructor

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
            raise TypeError('echoip.sources.IIPSource must be provided by source argument.')

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
        Round robin through the configured providers until one returns the keys
        required, then cache it
        :param required_info_keys: The keys required for the fetch to be valid
        :type required_info_keys: list(tuple)
        :return: The info dictionary returned by the provider
        :rtype: dict
        """
        if not self.is_cache_valid or not self._cache_info \
                or not self._verify_required_keys(self._cache_info, required_info_keys):
            self._cache_ip, self._cache_info = self._fetch_from_sources(required_info_keys)
            self._cache_timestamp = time.time()
        return self._cache_info

    def _fetch_from_sources(self, required_info_keys=None):
        """
        Internal method that fetches from configured sources.
        :param required_info_keys: Keys that are required in the response
        :type required_info_keys: list
        :return: None
        :rtype: None
        """
        srces = self._sources.keys()
        random.shuffle(srces)
        for source in srces:
            try:
                # noinspection PyProtectedMember
                source.fetch()

                ip_address = source.ip_address
                info = source.info

                if self._verify_required_keys(info, required_info_keys):
                    return ip_address, info

            except (ValueError, requests.ConnectionError):
                continue

        raise NullResponseFromSourcesError("No sources returned a valid response.")

    @staticmethod
    def _verify_required_keys(info, required_info_keys):
        """
        Private method to check that all keys required in an info response
        are provided.

        :param info: The dict to check for keys
        :type info: dict
        :param required_info_keys: a list of keys that are required. Lists or tuples
        provided in this list indicate that at least one key in the set must be present.
        :type required_info_keys: list(str, list(str))
        """
        keys_found = True
        if required_info_keys is not None:
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
        is_expired = time.time() - self._cache_timestamp < self._cache_ttl
        cache_info_set = self._cache_info is not None
        cache_ip_set = self._cache_ip is not None

        return is_expired and cache_info_set and cache_ip_set

    @property
    def num_sources(self):
        """
        Returns the number of configured sources in the provider
        """
        return len(self._sources)


class MultisourceIPProvider(IPProvider):
    """
    The IPProvider takes one or more IPSources and returns the results from
    them if the minimum number of sources are in agreement regard the external IP.
    Additional info from multiple providers is extended into one dictionary.
    If one provider does not respond it will move on to the next. It ensures
    that the age of the response on no older than the cache_ttl.
    """
    def __init__(self, source_list=None, cache_ttl=3600, min_source_agreement=2):
        """
        :param source_list: The list of sources to bootstrap the provider with
        :type source_list: list of IIPSource providers
        :param cache_ttl: the seconds the ip cache remains valid
        :param min_source_agreement: The minimum number of source that must be
        in agreement for an ip_fetch
        :type min_source_agreement: int
        """
        super(MultisourceIPProvider, self).__init__(source_list, cache_ttl)
        self._min_source_agreement = min_source_agreement

    def _fetch_from_sources(self, required_info_keys=None):
        if self.num_sources < self._min_source_agreement:
            raise InsufficientSourcesForAgreementError(
                "{} sources are required but only {} configured"
                .format(self._min_source_agreement, self.num_sources))
        infos = dict()
        ips = collections.defaultdict(list)
        srces = self._sources.keys()
        random.shuffle(srces)
        for source in srces:
            try:
                # noinspection PyProtectedMember
                source.fetch()
                ip_address = source.ip_address
                info = source.info

                if ip_address not in ips.keys():
                    ips[ip_address].append(source)
                    infos[source] = info
                else:
                    for src in ips[ip_address]:
                        info.update(infos[src])

                    if self._verify_required_keys(info, required_info_keys):
                        return ip_address, info
                    else:
                        infos[source] = source.info
            except (ValueError, requests.ConnectionError):
                continue

        raise InsufficientSourcesForAgreementError(
            "An insufficient number of sources were able to agree.")


class InsufficientSourcesForAgreementError(Exception):
    """
    Exception raised when there is not clear consensus
    among configured sources. This is often due to the
    minimum agreement argument.
    """
    pass


class NullResponseFromSourcesError(Exception):
    """
    Exception raised when no sources return a valid response
    """
    pass
