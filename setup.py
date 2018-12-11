'''setup.py'''
from setuptools import setup
setup(
    name='sacolbf',
    packages=['sacolbf'],
    version='0.12.1',
    description='Collector Library for bitFlyer',
    author='sabuaka',
    author_email='sabuaka-fx@hotmail.com',
    url="https://github.com/sabuaka/sacolbf",
    install_requires=[
        'numpy==1.14.4',
        'pandas==0.23.4',
        'sautility@git+https://github.com/sabuaka/sautility.git',
        'sabitflyer@git+https://github.com/sabuaka/sabitflyer.git'
    ],
)
