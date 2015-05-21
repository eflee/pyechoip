from setuptools import setup, find_packages

setup(
    name="pyechoip",
    version="1.3",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    
    include_package_data = True,
    install_requires=['mock>=1.0.1', 'ipaddress>=1.0', 'requests>=2.5.0', 'zope.interface>=4.1.1'],
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
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Other/Nonlisted Topic",
        ],
)
