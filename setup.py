from setuptools import setup, find_packages

setup(
    name = 'dsfxr',
    version='0.0.0',
    packages = find_packages(where='.'),
    install_requires = ['pyfxr @ git+https://github.com/wlaub/pyfxr.git@feature/stereo_buffers'],
    )
