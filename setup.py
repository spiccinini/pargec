#!/usr/bin/python
import glob
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pargec',
    version='0.1',
    author='Santiago Piccinini',
    author_email='san@satellogic.com',
    description='Generates C binary/protocol parsers (serializer and deserializer)',
    long_description=long_description,
    packages=[
        "pargec",
    ],
    scripts=glob.glob("bin/*"),
    install_requires=[
       'cffi>=1.2',
       'Jinja2>=2.8',
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    keywords=["protocol", "header", "parser", "binary", "C"]
)
