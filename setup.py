#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = open('README.md').read()

version = '0.1.10'
requirements = [
    'requests >= 2.4',
    'click >= 4.1',
    'python-geoip >= 1.2',
    'python-geoip-geolite2 >= 2015.303',
    'tabletext >= 0.1',
]

setup(
    name='weather-cli',
    version=version,
    install_requires=requirements,
    author='Fausto Carrera',
    author_email='fausto.carrera@gmx.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/faustocarrera/weather-cli',
    license='MIT',
    description='check the weather from the cli',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'weather-cli=weather:cli'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ]
)
