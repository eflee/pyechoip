import gimmeip.sources
from unittest import TestCase
import requests
import requests_mock
from ipaddress import IPv4Address
from mock import patch

__docformat__ = 'restructuredtext en'
__author__ = 'eflee'


class TestJSONBasedIPSource(TestCase):
    def setUp(self):
        self.source = gimmeip.sources.JSONBasedIPSource('https://fake-ip-url.com/', 'query')

    @requests_mock.Mocker()
    def test_ip_success(self, m):
        """Tests that a proper response from the URL yields the right interface"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsInstance(self.source.ip, IPv4Address, "IP address is parsable as IPv4")
        self.assertEquals(IPv4Address('127.0.0.1'), self.source.ip)

    @requests_mock.Mocker()
    def test_info_success(self, m):
        """Tests that a proper response from the URL yields no additional info (for this class)"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsInstance(self.source.info, dict, "Additional info should be a dict")
        self.assertEquals({'countryCode':'US'}, self.source.info)

    @requests_mock.Mocker()
    def test_bad_data(self, m):
        """Tests proper failure if crap data is returned"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text="Slartibartfast")
        with self.assertRaises(ValueError):
            self.source.refresh()
        with self.assertRaises(ValueError):
            # noinspection PyStatementEffect
            self.source.ip
        with self.assertRaises(ValueError):
            # noinspection PyStatementEffect
            self.source.info

    @patch('requests.get')
    def test_no_response(self, m):
        """Tests proper failure is a connection error occurs"""
        m.side_effect = requests.ConnectionError('ConnectionError')
        m.register_uri('GET', 'https://fake-ip-url.com/', text='Fail')
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.refresh()
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.ip
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.info

    @requests_mock.Mocker()
    def test_refresh_success(self, m):
        """Tests that the ip and info are unset until refresh happens"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsNone(self.source._ip)
        self.assertIsNone(self.source._info)
        self.source.refresh()
        self.assertIsNotNone(self.source.ip)
        self.assertIsNotNone(self.source.info)

    @requests_mock.Mocker()
    def test_auto_refresh_for_ip_property(self, m):
        """Tests that the ip property being none causes a refresh to happen transparently"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsNone(self.source._ip)
        self.assertIsNotNone(self.source.ip)

    @requests_mock.Mocker()
    def test_auto_refresh_for_info_property(self, m):
        """Tests that the info property being none causes a refresh to happen transparently"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsNone(self.source._info)
        self.assertIsNotNone(self.source.info)

    @requests_mock.Mocker()
    def test_refresh_preserve(self, m):
        """Tests that without a forced refresh the source returns the caches results"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertEquals(IPv4Address('127.0.0.1'), self.source.ip)
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.2"}')
        self.assertEquals(IPv4Address('127.0.0.1'), self.source.ip)
        self.source.refresh()
        self.assertEquals(IPv4Address('127.0.0.2'), self.source.ip)

