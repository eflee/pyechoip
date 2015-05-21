from setuptools import setup, find_packages

setup(
    name="pyechoip",
    version="1.2",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    
    include_package_data = True,
    install_requires=['mock>=1.0.1', 'py2-ipaddress>=2.0', 'requests>=2.5.0', 'zope.interface>=4.1.1'],
    tests_require=['requests-mock>=0.5.1'],
    test_suite='test',

    # metadata for upload to PyPI
    author="Eli Flesher",
    author_email="eli@eflee.us",
    description="A generic library for getting your externally visible IP address in python.",
    license="Apache",
    url="https://github.com/eflee/pyechoip",
    keywords=["ip", "network", "api"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Other/Nonlisted Topic",
        ],
)
