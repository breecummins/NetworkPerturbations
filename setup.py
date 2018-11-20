from setuptools import setup, find_packages

setup(
    name='NetworkPerturbations',
    version='0.0.1',
    packages=find_packages(exclude=["tests","examples",]),
    install_requires=[],
    author="Bree Cummins",
    url='https://github.com/breecummins/NetworkPerturbations'
    )