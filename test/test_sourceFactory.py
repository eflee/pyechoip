from unittest import TestCase
from gimmeip.sources import SourceFactory, SimpleIPSource, JSONBasedIPSource
import requests_mock

__docformat__ = 'restructuredtext en'
__author__ = 'eflee'


class TestSourceFactory(TestCase):
    def test_with_builtins(self):
        """Tests that builtins are accounted for by constructor and defaulted to included"""
        fac = SourceFactory(use_builtins=True)
        self.assertGreater(fac.num_sources, 0)
        self.assertEquals(len([x for x in fac.get_sources()]), fac.num_sources)  # Tests construction
        fac = SourceFactory()
        self.assertGreater(fac.num_sources, 0)
        self.assertEquals(len([x for x in fac.get_sources()]), fac.num_sources)  # Tests construction

    def test_no_builtins(self):
        """Tests that builtins can be disables by constructor"""
        fac = SourceFactory(use_builtins=False)
        self.assertEquals(fac.num_sources, 0)
        self.assertEquals(len([x for x in fac.get_sources()]), 0)  # Tests construction

    def test_get_sources_limit(self):
        """Tests that the limit function on get_sources works as documented"""
        fac = SourceFactory()
        self.assertEquals(len([x for x in fac.get_sources(5)]), 5)

    def test_filtering(self):
        """Tests that the type_filtering mechanism works with a list of types"""
        fac = SourceFactory()
        self.assertGreater(fac.num_sources, len([x for x in fac.get_sources(types_list=[SimpleIPSource])]))
        fac = SourceFactory()
        self.assertEqual(fac.num_sources, len([x for x in fac.get_sources(
            types_list=[SimpleIPSource, JSONBasedIPSource])]))

    def test_filtering_autobox_type(self):
        """Tests that the autoboxing of a type into a list works as advertised"""
        fac = SourceFactory()
        self.assertGreater(fac.num_sources, len([x for x in fac.get_sources(types_list=SimpleIPSource)]))

    @requests_mock.Mocker()
    def test_add_source(self, m):
        """Tests that adding a source works as advertised"""
        m.register_uri('GET', 'https://fake-ip-url.com/', text='127.0.0.1\n')
        m.register_uri('GET', 'https://fake-ip-json-url.com/', text='{"countryCode":"US", "query":"127.0.0.1"}')
        fac = SourceFactory(use_builtins=False)
        fac.add_source(SimpleIPSource, 'https://fake-ip-url.com/')
        fac.add_source(JSONBasedIPSource, 'https://fake-ip-json-url.com/', 'query')
        self.assertEquals(fac.num_sources, 2)
        self.assertEquals(len([x for x in fac.get_sources()]), 2)

    def test_get_sources(self):
        """Tests that all sources are returned by get_sources"""
        fac = SourceFactory()
        self.assertEquals(len([x for x in fac.get_sources()]), fac.num_sources)