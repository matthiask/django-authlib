#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='django-authlib',
    version=__import__('authlib').__version__,
    description='Authentication utils for Django',
    long_description=read('README.rst'),
    author='Matthias Kestenholz',
    author_email='mk@feinheit.ch',
    url='http://github.com/matthiask/django-authlib/',
    license='MIT License',
    platforms=['OS Independent'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests_oauthlib',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False,
)
