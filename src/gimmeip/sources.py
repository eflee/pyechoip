__docformat__ = 'restructuredtext en'
__author__ = 'eflee'

import copy
import random
import sys

import zope.interface
import requests
import ipaddress


class IIPSource(zope.interface.Interface):
    """
    The IPSource is an object that provides the IP address from an outside API. Any other information provided by the
    API is stores in the info dict.
    """

    ip = zope.interface.Attribute("""The current external IP address""")
    info = zope.interface.Attribute("""A Dict of any other information returned by the API""")

    # noinspection PyMethodMayBeStatic
    def refresh(self):
        """ Forces a refresh of the stored data """


class SimpleIPSource(object):
    zope.interface.implements(IIPSource)

    def __init__(self, ip_url):
        """
        Text Based IP Sources are intended for simple providers like curlmyip.com that return
        plain-text responses containing only the IP. The only mutation performed on this response is str.strip()
        to remove white space
        :param ip_url: The URL used to get the IP
        :type ip_url: str
        """
        self._ip_url = ip_url
        self._ip = None
        self._info = None

    @property
    def ip(self):
        """
        Returns the IP from source.
        :return: The IP
        :rtype: ipaddress.IPv4Address or ipaddress.IPv6Address
        """
        self.refresh()
        return copy.deepcopy(self._ip)

    @property
    def info(self):
        """
        Returns a dictionary containing any additional information returned by the API
        :return: any additional information returned by the API
        :rtype: dict
        """
        self.refresh()
        return self._info

    def refresh(self):
        """
        Performs a refresh from source
        :return: None
        :rtype: None
        """
        response = requests.get(self._ip_url)
        self._ip = ipaddress.ip_address(response.content.strip())
        self._info = dict()


class JSONIPSource(SimpleIPSource):
    zope.interface.implements(IIPSource)

    def __init__(self, ip_url, ip_key):
        """
        JSON Based IP Sources support providers that return JSON responses like ip-api.com.
        :param ip_url: The URL used to get the IP
        :type ip_url: str
        :param ip_key: The key in the json response used to encapsulate the IP
        :type ip_key: str
        """
        super(JSONIPSource, self).__init__(ip_url)
        self._ip_key = ip_key

    def refresh(self):
        """
        Performs a refresh from source
        :return: None
        :rtype: None
        """
        response = requests.get(self._ip_url)
        raw_response = response.json()
        raw_ip = raw_response[self._ip_key]
        if isinstance(raw_ip, (tuple, list)):
            raw_ip = raw_ip[0]
        self._ip = ipaddress.ip_address(raw_ip)
        self._info = raw_response
        del (self._info[self._ip_key])


class IPSourceFactory(object):
    _builtin_sources = {'ip-api.com': (JSONIPSource, 'http://ip-api.com/json', 'ip'),
                        'ifconfig.me': (JSONIPSource, 'http://ifconfig.me/all.json', 'ip_addr'),
                        'ifconfig.co': (JSONIPSource, 'http://ifconfig.co/all.json', 'X-Real-Ip'),
                        'ipinfo.io': (JSONIPSource, 'http://ipinfo.io/json', 'ip'),
                        'ipinfo.org': (JSONIPSource, 'http://ipinfo.org/json', 'ip'),
                        'trackip.net': (JSONIPSource, 'http://www.trackip.net/ip?json', 'ip'),
                        'httpbin.org': (JSONIPSource, 'http://httpbin.org/get', 'origin'),
                        'wtfismyip.com': (JSONIPSource, 'http://wtfismyip.com/json', 'YourFuckingIPAddress'),
                        'ipecho.net': (SimpleIPSource, 'http://ipecho.net/plain'),
                        'eth0.me': (SimpleIPSource, 'http://eth0.me/'),
                        'ip.appstop.com': (SimpleIPSource, 'http://ip.appspot.com/'),
                        'l2.io': (SimpleIPSource, 'http://l2.io/ip'),
                        'curlmyip.com': (SimpleIPSource, 'http://curlmyip.com/'),
                        'icanhazip.com': (SimpleIPSource, 'http://icanhazip.com/'),
    }

    def __init__(self, use_builtins=True):
        """
        A Factory that can be used to generate IIPSource providers
        :param use_builtins: there are a number of built-in sources available in this library, this option includes
        them by default in the factory.
        :type use_builtins: bool
        """
        self._sources = set()
        if use_builtins:
            for v in self._builtin_sources.values():
                self.add_source(*v)

    def add_source(self, source_class, *constructor_args):
        """
        Adds a source to the factory provided it's type and constructor arguments
        :param source_class: The class used to instantiate the source
        :type source_class: type
        :param constructor_args: Arguments to be passed into the constructor
        :type constructor_args: Iterable
        """
        if not IIPSource.implementedBy(source_class):
            raise TypeError("source_class {} must implement IIPSource".format(source_class))
        else:
            self._sources.add((source_class, constructor_args))

    def get_sources(self, limit=sys.maxint, types_list=None):
        """
        Generates instantiated sources from the factory
        :param limit: the max number of sources to yield
        :type limit: int
        :param types_list: filter by types so the constructor can be used to accomidate many types
        :type types_list: class or list of classes
        :return: Yields types added by add_source
        :rtype: generator
        """
        if types_list and not isinstance(types_list, (tuple, list)):
            types_list = [types_list]

        sources = list(self._sources)
        random.shuffle(sources)

        for source in sources:
            if not types_list or source[0] in types_list:
                limit -= 1
                yield source[0](*source[1])

            if limit <= 0:
                break

    @property
    def num_sources(self):
        """
        :return: The number of configured sources
        :rtype: int
        """
        return len(self._sources)
