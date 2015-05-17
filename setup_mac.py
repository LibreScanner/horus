#!/usr/bin/python
# coding=utf-8

import os
from setuptools import setup, find_packages

def package_data_dirs(source, sub_folders):
    dirs = []

    for d in sub_folders:
        for dirname, _, files in os.walk(os.path.join(source, d)):
            dirname = os.path.relpath(dirname, source)
            for f in files:
                dirs.append(os.path.join(dirname, f))
    return dirs

DATA_FILES = ['doc','res']

OPTIONS = {'argv_emulation': True,
           'iconfile': 'res/horus.icns'}

setup(name='Horus',
      version='0.1.1.1',
      author='Jesús Arroyo Torrens',
      author_email='jesus.arroyo@bq.com',
      description='Horus is a full software solution for 3D scanning',
      license='GPLv2',
      keywords="horus ciclop scanning 3d",
      url='https://www.diwo.bq.com/tag/ciclop',
      options={'py2app': OPTIONS},
      setup_requires=['py2app'],
      app=['src/horus.py'],
      data_files=DATA_FILES)
