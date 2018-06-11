from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.read()
install_requires = list(
    filter(lambda x: len(x) > 0, install_requires.split('\n')))

setup(
    name='bothub',
    version='1.8.8',
    description='bothub',
    packages=find_packages(),
    install_requires=install_requires,
    python_requires='>=3.6',
)
