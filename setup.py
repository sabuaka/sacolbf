'''setup.py'''
from setuptools import setup
setup(
    name='sacolbf',
    packages=['sacolbf'],
    version='0.12.2',
    description='Collector Library for bitFlyer',
    author='sabuaka',
    author_email='sabuaka-fx@hotmail.com',
    url="https://github.com/sabuaka/sacolbf",
    install_requires=[
        'numpy==1.14.4',
        'pandas==0.23.4',
        'ntplib==0.3.3',
        'sautility@git+https://github.com/sabuaka/sautility.git',
        'sabitflyer@git+https://github.com/sabuaka/sabitflyer.git'
    ],
)
