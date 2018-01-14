#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Setup configuration for `pullbot`.

'''
import re
import sys
import versioneer

from pullbot import __version__, __author__, __license__, __email__

from os import path as p

try:
    from setuptools import setup, find_packages

except ImportError:
    from distutils.core import setup


def read(filename, parent=None):
    '''
    Reads a text file into memory.

    '''
    parent = (parent or __file__)

    try:
        with open(p.join(p.dirname(parent), filename)) as f:
            return f.read()

    except IOError:
        return ''


def parse_requirements(filename, parent=None, dep=False):
    '''
    Parse requirements from *.txt files. Make sure to
    handle git variations.

    '''
    parent = (parent or __file__)
    filepath = p.join(p.dirname(parent), filename)
    content = read(filename, parent)

    for line_number, line in enumerate(content.splitlines(), 1):
        candidate = line.strip()

        if candidate.startswith('-r'):
            args = [candidate[2:].strip(), filepath, dep]

            for item in parse_requirements(*args):
                yield item

        elif not dep and '#egg=' in candidate:
            yield re.sub('.*#egg=(.*)-(.*)', r'\1==\2', candidate)
        elif dep and '#egg=' in candidate:
            yield candidate.replace('-e ', '')
        elif not dep:
            yield candidate

#
#  Controls byte-compiling the shipped template.
#
sys.dont_write_bytecode = False

#
#  Parse all requirements.
#
requirements = list(parse_requirements('requirements.txt'))
dependencies = list(parse_requirements('requirements.txt', dep=True))
readme = read('README.md')

setup(

    name='pullbot',
    version=__version__,
    cmdclass=versioneer.get_cmdclass(),
    description='GitHub PR automation',
    long_description=readme,
    py_module=['pullbot'],

    entry_points={
        'console_scripts': [
            'pullbot = pullbot.pullbot:main'
        ]
    },

    author=__author__,
    author_email=__email__,
    url='https://github.com/greenape/pullbot',

    license=__license__,
    keywords='cdr etl',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=dependencies,
    dependency_links=dependencies,
    include_package_data=True,
    zip_safe=False,
    platforms=['MacOS X', 'Linux'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
    ]
)
