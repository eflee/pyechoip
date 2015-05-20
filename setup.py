from setuptools import setup, find_packages

setup(
    name="pyechoip",
    version="1.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    
    install_requires=['mock>=1.0.1', 'py2-ipaddress>=2.0', 'requests>=2.5.0', 'zope.interface>=4.1.1'],
    tests_require=['requests-mock>=0.5.1'],

    include_package_data = True,

    # metadata for upload to PyPI
    author="Eli Flesher",
    author_email="eli@eflee.us",
    description="A generic library for getting your externally visible IP address in python.",
    license="Apache",
    keywords="ip network",
    url="https://github.com/eflee/pyechoip",  # project home page, if any
    test_suite='test',
)
