#!/bin/bash

# remove installation in user directory

rm -rf ~/.local/lib/python3.6/site-packages/slidenc-0.1-py3.6.egg

# in case it was installed with in development mode with
# python setup.py  develop --user
# see https://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode
rm -rf ~/.local/lib/python3.6/site-packages/slidenc.egg-link


rm -rf slidenc.egg-info
rm -rf build
rm -rf dist
rm ~/.local/bin/slidenc
