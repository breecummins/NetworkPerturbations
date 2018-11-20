from distutils.core import setup

setup(
    name='NetworkPerturbations',
    version='0.0.1',
    package_dir={'':'lib'},
    packages = ['NetworkPerturbations','NetworkPerturbations.perturbations','NetworkPerturbations.queries','NetworkPerturbations.min_interval_posets.libposets'],
    install_requires=[],
    author="Bree Cummins",
    url='https://github.com/breecummins/NetworkPerturbations'
    )