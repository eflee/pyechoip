PyEchoIP
=========

A generic library in python to get your external IP from sites around 
the internet in a consistent manner. Using zopes interfaces, allows the 
user to create their own sources. Features time-based caching, multi-source
verification and other features.

Using IP Providers
------------------

IP providers are the high-level interfaces to IPSources. They allow the user an
abstraction from the source provider and in fact allow them to use multiple 
sources transparently.

By default all providers cache a response from one hour (3600 seconds) and will
self-invalidate in the event that time passes or the users requests an
additional information key that is not present in the current cache. 

Note: because different sources return different supplement information to the IP
address, the users must know the key for which they're looking in order to make
use of the information. This is one of the rougher edges of the code base 
because it is on the boundary of the intended scope. If you need a feature, 
please ask for it.

### IPProvider

The standard IPProvider checks a single source, provides and caches the answer. 

```
    In [1]: import echoip
    In [2]: import echoip.sources
    In [3]: import echoip.providers
    In [4]: source_factory = echoip.sources.IPSourceFactory()
    In [5]: provider = echoip.providers.IPProvider()
    In [6]: for source in source_factory.get_sources():
       ...:     provider.add_source(source)
       ...:
    In [7]: provider.get_ip()
    Out[7]: IPv4Address('67.171.19.153')
```

Usage:

    Type:            type
    String form:     <class 'echoip.providers.IPProvider'>
    Init definition: echoip.providers.IPProvider(self, source_list=None, cache_ttl=3600)
    Init docstring:
    The IPProvider takes one or more IPSources and returns the results from them . If one
    provider does not respond it will move on to the next. It ensures that the age of the
    response on no older than the cache_ttl.
    
    :param source_list: The list of sources to bootstrap the provider with
    :type source_list: list of IIPSource providers
    :param cache_ttl: the seconds the ip cache remains valid
    :type cache_ttl: int
    
Some sources choose to provide additional information (like GeoIP information). 
That information is marshalled into a single dictionary based and can be
retrieved by get_info():

```
    In [8]: provider.get_info()
    Out[8]:
    {u'city': u'Keb',
     u'country': u'CO',
     u'loc': u'27.6355,-22.3235'}
```

Further documenation: 

### MultipleSourceIPProvider

The MultipleSourceIPProvider checks with multiple sources. If and only if 
min_source_agreement (constructor parameter) sources agree on the IP address is
the answer cached.

Note: The IP is cached. The additional info from the sources are combined into
a single dictionary. Duplicate keys are overwritten in a non-deterministic
fashion. This provider is mostly useful for when you are distrustful of the IP
results. 

The provider is used the exact same way. 

```
    In [1]: import echoip
    In [2]: import echoip.sources
    In [3]: import echoip.providers
    In [4]: source_factory = echoip.sources.IPSourceFactory()
    In [5]: provider = echoip.providers.MultisourceIPProvider
    In [6]: for source in source_factory.get_sources():
       ...:     provider.add_source(source)
       ...:
    In [7]: provider.get_ip()
    Out[7]: IPv4Address('67.171.19.153')
```

Usage: 

    Type:            type
    String form:     <class 'echoip.providers.MultisourceIPProvider'>
    File:            /Users/eflee/Development/pyechoip/src/echoip/providers.py
    Init definition: echoip.providers.MultisourceIPProvider(self, source_list=None, cache_ttl=3600, min_source_agreement=2)
    Init docstring:
    The IPProvider takes one or more IPSources and returns the results from them if the minimum number of sources
    are in agreement regard the external IP.
    Additional info from multiple providers is extended into one dictionary.
    If one provider does not respond it will move on to the next. It ensures that the age of the
    response on no older than the cache_ttl.
    
    :param source_list: The list of sources to bootstrap the provider with
    :type source_list: list of IIPSource providers
    :param cache_ttl: the seconds the ip cache remains valid
    :param min_source_agreement: The minimum number of source that must be in agreement for an ip_fetch
    :type min_source_agreement: int
    
Further documenation: 

Using IP Sources
----------------

IPSources are the low-level interface to the library. There is no caching for 
IPSources and the only validation is the returned IP address.

There are two (as of now) basic types: SimpleIPSources and 
JSONIPSources which seem to be the two most common interface types for the
publicly available services. 

In addition to IPSources there is an IPSourceFactory that can generate 
configured sources for the list of built-ins below.

Finally, there is an IIPSource interface for implementing customer sources. 

### IIPSource (Interface)

I want to cover this in brief, this is the interface for implementing custom 
sources. It is rather simple: the source must provide an ip attribute and an 
info attribute.

The ip attribute is the ipaddress.IPv4Address or ipaddress.IPv6Address 
(py2-ipaddress for Python2 or ipaddress for Python3) encapsulated ip address 
returned from the API.

The info attribute is a key-value dictionary for all other results returned from
the API. There is no additional guarantees of cleanliness or format and this 
varries from source to source.

### SimpleIPSource

The SimpleIPSource handles sites like curlmyip.com that return only an string
IP. The class simply strips the whitespace from the string and validates it 
by instantiating it as an IPAddress.

```
    In [1]: import echoip.sources
    In [2]: source = echoip.sources.SimpleIPSource('http://curlmyip.com/')
    In [3]: source.ip
    Out[3]: IPv4Address('67.171.19.153')
```

The info attribute on this IPSource type is always empty.

### JSONIPSource

The JSONIPSource handles sites like ip-api.com that provide a more complete
API (obviousely a JSON API). The class takes a json key to select the IP and 
then uses the same validation as the SimpleIPSource class. All other results
returned by the API are boxed into a dict that is returned by the info 
attribute.

```
    In [1]: import echoip.sources
    In [2]: source = echoip.sources.JSONIPSource('http://ip-api.com/json', 'query')
    In [3]: source.ip
    Out[3]: IPv4Address('67.171.19.153')
    In [4]: source.info
    Out[4]:
    {u'city': u'Keb',
     u'country': u'CO',
     u'loc': u'27.6355,-22.3235'}
```

### IPSourceFactory

The IPSourceFactory is a utility class that has two purposes. One, it allows the
user to create instances based on their own resources using the provided source
types. Two, it allows the user to instantiate with all of the built-in sites.

Instantiating with custom resources:

```
    In [1]: import echoip.sources
    In [2]: fac = echoip.sources.IPSourceFactory(use_builtins=False)
    In [3]: fac.add_source(echoip.sources.SimpleIPSource, 'http://10.0.0.1')
    In [4]: fac.add_source(echoip.sources.JSONIPSource, 'http://10.0.0.2', 'ip')
    In [5]: fac.num_sources
    Out[5]: 2
    In [6]: [ src for src in fac.get_sources() ]
    Out[6]:
    [<echoip.sources.SimpleIPSource at 0x10bb5d390>,
    <echoip.sources.JSONIPSource at 0x10bb5d3d0>]
```

Instantiation with built-ins (default):
    
```
    In [1]: import echoip.sources
    In [2]: fac = echoip.sources.IPSourceFactory()
    In [3]: fac.num_sources
    Out[3]: 14
    In [4]: [ src for src in fac.get_sources() ]
    Out[4]:
    [<echoip.sources.JSONIPSource at 0x102f6b510>,
    <echoip.sources.JSONIPSource at 0x102f6b550>,
    <echoip.sources.JSONIPSource at 0x102f6b590>,
    ...
    <echoip.sources.SimpleIPSource at 0x102f6b850>]
```


Built-in Sources
----------------

Users of this library who choose to use the default sources are subject to the
terms and limitations of those sources and are responsible for their conduct
when using these services. 

[List of Sources and their Maintainters](THANKS.md)
