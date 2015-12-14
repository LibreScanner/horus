#!/usr/bin/python
# coding=utf-8

import os
from setuptools import setup, find_packages

version = '0.2b1'  # os.environ.get('VERSION')


def package_data_dirs(source, basedir='/usr/share/horus'):
    dirs = []

    for dirname, _, files in os.walk(source):
        dirname = os.path.relpath(dirname, source)
        for f in files:
            dirs.append((os.path.join(basedir, dirname),
                         [os.path.join(source, dirname, f)]))

    # dirs.append(('/usr/share/applications', ['pkg/linux/horus.desktop']))

    return dirs


setup(
    name='Horus',
    version=version,
    author='Jesús Arroyo Torrens',
    author_email='jesus.arroyo@bq.com',
    description='Horus is a full software solution for 3D scanning',

    license='GPLv2',
    keywords="horus ciclop scanning 3d",
    url='https://www.diwo.bq.com',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    scripts=['horus'],
    data_files=package_data_dirs('res'),
)
