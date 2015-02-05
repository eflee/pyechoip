__docformat__ = 'restructuredtext en'
__author__ = 'Eli Flesher <eli@eflee.us>'

import unittest

import requests
import requests_mock
import ipaddress
import mock

import echoip.sources


class TestTextBasedIPSource(unittest.TestCase):
    def setUp(self):
        self.source = echoip.sources.SimpleIPSource('https://fake-ip-url.com/')

    @requests_mock.Mocker()
    def test_ip_success(self, m):
        """Tests that a proper response from the URL yields the right interface"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        self.assertIsInstance(self.source.ip, ipaddress.IPv4Address, "IP address is parsable as IPv4")
        self.assertEquals(ipaddress.IPv4Address('127.0.0.1'), self.source.ip)

    @requests_mock.Mocker()
    def test_info_success(self, m):
        """Tests that a proper response from the URL yields no additional info (for this class)"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        self.assertIsInstance(self.source.info, dict, "Additional info should be a dict")
        self.assertEquals({}, self.source.info)

    @requests_mock.Mocker()
    def test_bad_data(self, m):
        """Tests proper failure if crap data is returned"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text="Slartibartfast")
        with self.assertRaises(ValueError):
            self.source._fetch()
        with self.assertRaises(ValueError):
            # noinspection PyStatementEffect
            self.source.ip
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
            self.source._fetch()
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.ip
        with self.assertRaises(requests.ConnectionError):
            # noinspection PyStatementEffect
            self.source.info

    @requests_mock.Mocker()
    def test_refresh_success(self, m):
        """Tests that the ip and info are unset until refresh happens"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        self.assertIsNone(self.source._ip)
        self.assertIsNone(self.source._info)
        self.source._fetch()
        self.assertIsNotNone(self.source.ip)
        self.assertIsNotNone(self.source.info)

    @requests_mock.Mocker()
    def test_auto_refresh_for_ip_property(self, m):
        """Tests that the ip property being none causes a refresh to happen transparently"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        self.assertIsNone(self.source._ip)
        self.assertIsNotNone(self.source.ip)

    @requests_mock.Mocker()
    def test_auto_refresh_for_info_property(self, m):
        """Tests that the info property being none causes a refresh to happen transparently"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        self.assertIsNone(self.source._info)
        self.assertIsNotNone(self.source.info)

