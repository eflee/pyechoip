from unittest import TestCase
from gimmeip.sources import SourceFactory, SimpleIPSource, JSONIPSource
from gimmeip.providers import MultisourceIPProvider, InsufficientSourcesForAgreementError
import requests_mock
from ipaddress import IPv4Address
import time
import requests
__docformat__ = 'restructuredtext en'
__author__ = 'eflee'


class TestMultisourceIPProvider(TestCase):
    @requests_mock.Mocker()
    def test_add_source(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertEquals(fac.num_sources, ipp.num_sources)

    @requests_mock.Mocker()
    def test_get_ip(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.1'))

    @requests_mock.Mocker()
    def test_get_ip_non_agreement(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.2\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertRaises(InsufficientSourcesForAgreementError, ipp.get_ip)

    @requests_mock.Mocker()
    def test_get_info(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        m.register_uri('GET', 'https://fake-ip-json-url2.com/', text='{"countryCode2":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url2.com/', 'query')

        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertEquals(ipp.get_info(), {'countryCode': 'US', 'countryCode2': 'US'})

    @requests_mock.Mocker()
    def test_get_info_non_agreement(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        m.register_uri('GET', 'https://fake-ip-json-url2.com/', text='{"countryCode2":"US", "query":"127.0.0.2"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url2.com/', 'query')

        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)
        self.assertRaises(InsufficientSourcesForAgreementError, ipp.get_info)



    @requests_mock.Mocker()
    def test_get_info_with_required_keys(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        m.register_uri('GET', 'https://fake-ip-json-url2.com/', text='{"whoami":"US", "whoami2":"US", "anykey1":"1", \
                                                                      "query":"127.0.0.1"}')

        fac = SourceFactory(use_builtins=False)
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url2.com/', 'query')

        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)

        self.assertEquals(ipp.get_info(required_info_keys=['whoami', 'whoami2']),
                          {u'whoami2': u'US', u'whoami': u'US', u'countryCode': u'US', u'anykey1': u'1'})

    @requests_mock.Mocker()
    def test_get_info_with_required_keys_and_subkeys(self, m):
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        m.register_uri('GET', 'https://fake-ip-json-url2.com/', text='{"whoami":"US", "whoami2":"US", "anykey1":"1", \
                                                                      "query":"127.0.0.1"}')

        fac = SourceFactory(use_builtins=False)
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url2.com/', 'query')

        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)

        self.assertEquals(ipp.get_info(required_info_keys=[['anykey1', 'anykey2']]),
                          {u'whoami2': u'US', u'whoami': u'US', u'countryCode': u'US', u'anykey1': u'1'})

    @requests_mock.Mocker()
    def test_invalidate_cache(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)

        self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.1'))
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.2\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.2"}')
        ipp.invalidate_cache()
        self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.2'))

    @requests_mock.Mocker()
    def test_invalidate_cache_non_agreement(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = MultisourceIPProvider()
        for source in fac.get_sources():
            ipp.add_source(source)

        with self.assertRaises(InsufficientSourcesForAgreementError):
            self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.1'))
            m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
            m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.2"}')
            ipp.invalidate_cache()
            self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.2'))

    @requests_mock.Mocker()
    def test_cache(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = MultisourceIPProvider(cache_ttl=2)
        for source in fac.get_sources():
            ipp.add_source(source)

        timestamp = time.time()
        self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.1'))
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.2\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.2"}')

        self.assertTrue(ipp.is_cache_valid())
        while time.time() - timestamp < 3:
            time.sleep(0.5)
        self.assertFalse(ipp.is_cache_valid())

        self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.2'))

    @requests_mock.Mocker()
    def test_cache_non_agreement(self, m):
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        ipp = MultisourceIPProvider(cache_ttl=2)
        for source in fac.get_sources():
            ipp.add_source(source)

        timestamp = time.time()
        self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.1'))
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.2"}')

        with self.assertRaises(InsufficientSourcesForAgreementError):
            self.assertTrue(ipp.is_cache_valid())
            while time.time() - timestamp < 3:
                time.sleep(0.5)
            self.assertFalse(ipp.is_cache_valid())
            self.assertEquals(ipp.get_ip(), IPv4Address('127.0.0.2'))
