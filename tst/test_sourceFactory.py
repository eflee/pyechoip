__docformat__ = 'restructuredtext en'
__author__ = 'Eli Flesher <eli@eflee.us>'

import unittest

import requests_mock

import echoip.sources


class TestSourceFactory(unittest.TestCase):
    def test_empty_source(self):
        """Tests construction has no sources"""
        fac = echoip.sources.IPSourceFactory()
        self.assertEquals(fac.num_sources, 0)
        self.assertEquals(len([x for x in fac.get_sources()]), 0)  # Tests construction

    def test_get_sources_limit(self):
        """Tests that the limit function on get_sources works as documented"""
        fac = echoip.sources.IPSourceFactory()
        fac.add_source(echoip.sources.SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        self.assertEquals(len([x for x in fac.get_sources(2)]), 2)

    def test_filtering(self):
        """Tests that the type_filtering mechanism works with a list of types"""
        fac = echoip.sources.IPSourceFactory()
        fac.add_source(echoip.sources.SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        self.assertGreater(fac.num_sources, len([x for x in fac.get_sources(types_list=[echoip.sources.SimpleIPSource])]))
        self.assertEqual(fac.num_sources, len([x for x in fac.get_sources(
            types_list=[echoip.sources.SimpleIPSource, echoip.sources.JSONIPSource])]))

    def test_filtering_autobox_type(self):
        """Tests that the autoboxing of a type into a list works as advertised"""
        fac = echoip.sources.IPSourceFactory()
        fac.add_source(echoip.sources.SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        self.assertGreater(fac.num_sources, len([x for x in fac.get_sources(types_list=echoip.sources.SimpleIPSource)]))

    @requests_mock.Mocker()
    def test_add_source(self, m):
        """Tests that adding a source works as advertised"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = echoip.sources.IPSourceFactory()
        fac.add_source(echoip.sources.SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(echoip.sources.JSONIPSource, 'https://fake-ip-json-url.com/', 'query')
        self.assertEquals(fac.num_sources, 2)
        self.assertEquals(len([x for x in fac.get_sources()]), 2)

    def test_get_sources(self):
        """Tests that all sources are returned by get_sources"""
        fac = echoip.sources.IPSourceFactory()
        self.assertEquals(len([x for x in fac.get_sources()]), fac.num_sources)