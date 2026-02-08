# -*- coding: utf-8 -*-

import sys

from setuptools import setup

import mutpy

if sys.version_info[:2] < (3, 7):
    print('MutPy fork requires Python 3.7 or newer!')
    sys.exit(1)

with open('requirements/production.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='MutPy-37plus',
    version=mutpy.__version__,
    python_requires='>=3.7',
    description='A fork of MutPy for Python 3.7+ source code.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Konrad Hałas',
    author_email='halas.konrad@gmail.com',
    maintainer='prdktntwcklr',
    maintainer_email='61001903+prdktntwcklr@users.noreply.github.com',
    url='https://github.com/prdktntwcklr/mutpy',
    download_url='https://github.com/prdktntwcklr/mutpy',
    packages=['mutpy', 'mutpy.operators', 'mutpy.test_runners'],
    package_data={'mutpy': ['templates/*.html']},
    scripts=['bin/mut.py'],
    install_requires=requirements,
    extras_require={
        'pytest': ["pytest>=3.0"]
    },
    test_suite='mutpy.test',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
    ],
)
