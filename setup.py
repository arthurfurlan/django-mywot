#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-mywot',
    version='0.1',
    url='http://github.com/valvim/django-mywot',
    license='GPLv3',
    description='Django application that consumes the MyWOT API and keeps a local cache.',
    author='Arthur Furlan',
    long_description=read('README'),
    author_email='afurlan@valvim.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
