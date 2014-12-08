__docformat__ = 'restructuredtext en'
__author__ = 'eflee'

import zope.interface
import requests
import ipaddress
import copy
import random


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
        if self._ip is None:
            self.refresh()
        return copy.deepcopy(self._ip)

    @property
    def info(self):
        """
        Returns a dictionary containing any additional information returned by the API
        :return: any additional information returned by the API
        :rtype: dict
        """
        if self._info is None:
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

class JSONBasedIPSource(SimpleIPSource):
    zope.interface.implements(IIPSource)

    def __init__(self, ip_url, ip_key):
        """
        JSON Based IP Sources support providers that return JSON responses like ip-api.com.
        :param ip_url: The URL used to get the IP
        :type ip_url: str
        :param ip_key: The key in the json response used to encapsulate the IP
        :type ip_key: str
        """
        super(JSONBasedIPSource, self).__init__(ip_url)
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
        if isinstance((tuple, list), raw_ip):
            raw_ip = raw_ip[0]
        self._ip = ipaddress.ip_address(raw_ip)
        if self
        self._info = raw_response
        del(self._info[self._ip_key])