from setuptools import setup, find_packages

setup(
    name="pygimmeip",
    version="0.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    
    install_requires=[],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst']
    },

    # metadata for upload to PyPI
    author="Eli Flesher",
    author_email="eli@eflee.us",
    description="A generic library for getting your externally visible IP address in python.",
    license="Apache",
    keywords="ip network",
    url="http://elif.us/pygimmeip",  # project home page, if any
    test_suite='test',
)
