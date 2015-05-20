__docformat__ = 'restructuredtext en'
__author__ = 'Eli Flesher <eli@eflee.us>'

import unittest

import requests
import requests_mock
import ipaddress
import mock

import echoip.sources


class TestJSONBasedIPSource(unittest.TestCase):
    def setUp(self):
        self.source = echoip.sources.JSONIPSource('https://fake-ip-url.com/', 'query')

    @requests_mock.Mocker()
    def test_ip_success(self, m):
        """Tests that a proper response from the URL yields the right interface"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode": "US", "query": "127.0.0.1"}')
        self.assertIsInstance(self.source.ip_address, ipaddress.IPv4Address, "IP address is parsable as IPv4")
        self.assertEquals(ipaddress.IPv4Address('127.0.0.1'), self.source.ip_address)

    @requests_mock.Mocker()
    def test_info_success(self, m):
        """Tests that a proper response from the URL yields no additional info (for this class)"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode": "US", "query": "127.0.0.1"}')
        self.assertIsInstance(self.source.info, dict, "Additional info should be a dict")
        self.assertEquals({'countryCode': 'US'}, self.source.info)

    @requests_mock.Mocker()
    def test_bad_data(self, m):
        """Tests proper failure if crap data is returned"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text="Slartibartfast")
        with self.assertRaises(ValueError):
            self.source.fetch()
        with self.assertRaises(ValueError):
            # noinspection PyStatementEffect
            self.source.ip_address
        with self.assertRaises(ValueError):
            # noinspection PyStatementEffect
            self.source.info

    @mock.patch('requests.get')
    def test_no_response(self, m):
        """Tests proper failure is a connection error occurs"""
        m.side_effect = requests.ConnectionError('ConnectionError')
        m.register_uri('GET', 'https://fake-ip-url.com/', text='Fail')
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.fetch()
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.ip_address
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.info

    @requests_mock.Mocker()
    def test_refresh_success(self, m):
        """Tests that the ip and info are unset until refresh happens"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsNone(self.source._ip_address)
        self.assertIsNone(self.source._info)
        self.source.fetch()
        self.assertIsNotNone(self.source.ip_address)
        self.assertIsNotNone(self.source.info)

    @requests_mock.Mocker()
    def test_auto_refresh_for_ip_property(self, m):
        """Tests that the ip property being none causes a refresh to happen transparently"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsNone(self.source._ip_address)
        self.assertIsNotNone(self.source.ip_address)

    @requests_mock.Mocker()
    def test_auto_refresh_for_info_property(self, m):
        """Tests that the info property being none causes a refresh to happen transparently"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        self.assertIsNone(self.source._info)
        self.assertIsNotNone(self.source.info)

