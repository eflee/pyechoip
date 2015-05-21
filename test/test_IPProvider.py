__docformat__ = 'restructuredtext en'
__author__ = 'Eli Flesher <eli@eflee.us>'

import unittest
import time

import requests_mock
import ipaddress
import mock
import requests

import echoip.sources
import echoip.providers


class TestIPProvider(unittest.TestCase):
    @requests_mock.Mocker()
    def test_add_source(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = echoip.sources.IPSourceFactory(use_builtins=False)
        fac.add_source(echoip.sources.SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = echoip.providers.IPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertEquals(fac.num_sources, ipp.num_sources)

    @requests_mock.Mocker()
    def test_get_ip(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = echoip.sources.IPSourceFactory(use_builtins=False)
        fac.add_source(echoip.sources.SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = echoip.providers.IPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertEquals(ipp.get_ip(), ipaddress.IPv4Address(u'127.0.0.1'))

    @requests_mock.Mocker()
    def test_get_info(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode": "US", "query": "127.0.0.1"}')
        fac = echoip.sources.IPSourceFactory(use_builtins=False)
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = echoip.providers.IPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertEquals(ipp.get_info(), {'countryCode': 'US'})

    @mock.patch('requests.get')
    def test_no_response(self, m):
        """Tests proper failure if a connection error occurs"""
        m.side_effect = requests.ConnectionError('ConnectionError')
        m.register_uri('GET', 'https://fake-ip-url.com/', text='Fail')
        with self.assertRaises(echoip.providers.NullResponseFromSourcesError):
            fac = echoip.sources.IPSourceFactory(use_builtins=False)
            fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-url.com/', 'query')
            ipp = echoip.providers.IPProvider()
            for source in fac.get_sources():
                ipp.add_source(source)
            self.assertEquals(ipp.get_ip(), ipaddress.IPv4Address(u'127.0.0.1'))

    @requests_mock.Mocker()
    def test_get_info_with_required_keys(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        m.register_uri('GET', 'https://fake-ip-json-url2.com/', text='{"whoami":"US", "whoami2":"US", "anykey1":"1", \
                                                                      "query":"127.0.0.1"}')

        fac = echoip.sources.IPSourceFactory(use_builtins=False)
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url2.com/', 'query')

        ipp = echoip.providers.IPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)

        self.assertEquals(ipp.get_info(required_info_keys=['whoami', 'whoami2']),
                          {u'whoami2': u'US', u'whoami': u'US', u'anykey1': u'1'})

    @requests_mock.Mocker()
    def test_get_info_with_required_keys_and_subkeys(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        m.register_uri('GET', 'https://fake-ip-json-url2.com/', text='{"whoami":"US", "whoami2":"US", "anykey1":"1", \
                                                                      "query":"127.0.0.1"}')

        fac = echoip.sources.IPSourceFactory(use_builtins=False)
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url2.com/', 'query')

        ipp = echoip.providers.IPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)

        self.assertEquals(ipp.get_info(required_info_keys=[['anykey1', 'anykey2']]),
                          {u'whoami2': u'US', u'whoami': u'US', u'anykey1': u'1'})

    @requests_mock.Mocker()
    def test_invalidate_cache(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = echoip.sources.IPSourceFactory(use_builtins=False)
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = echoip.providers.IPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)

        self.assertEquals(ipp.get_ip(), ipaddress.IPv4Address(u'127.0.0.1'))
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.2"}')
        ipp.invalidate_cache()
        self.assertEquals(ipp.get_ip(), ipaddress.IPv4Address(u'127.0.0.2'))

    @requests_mock.Mocker()
    def test_cache(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = echoip.sources.IPSourceFactory(use_builtins=False)
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = echoip.providers.IPProvider(cache_ttl=2)
        for source in fac.get_sources():
            ipp.add_source(source)

        timestamp = time.time()
        self.assertEquals(ipp.get_ip(), ipaddress.IPv4Address(u'127.0.0.1'))
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.2"}')

        self.assertTrue(ipp.is_cache_valid())
        while time.time() - timestamp < 3:
            time.sleep(0.5)
        self.assertFalse(ipp.is_cache_valid())

        self.assertEquals(ipp.get_ip(), ipaddress.IPv4Address(u'127.0.0.2'))
