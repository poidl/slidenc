"""Setup script"""
from setuptools import setup, find_packages
setup(
    name="slidenc",
    version="0.1",
    packages=find_packages(exclude=(
        'tmp', 'build', 'dist', 'slidenc.egg-info' 'tests', 'docs')),
    entry_points={
        'console_scripts': [
            'slidenc = slidenc.slidenc:main',
        ],
    },
    include_package_data=True
)
