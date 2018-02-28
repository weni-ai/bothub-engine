from setuptools import setup, find_packages
from os import path

with open('requirements.txt') as fp:
    install_requires = fp.read()
install_requires = filter(lambda x: len(x) > 0, install_requires.split('\n'))

setup(
    name='bothub-app',
    version='0.1.1',
    description='bothub app',
    packages=find_packages(),
    install_requires=install_requires,
)
