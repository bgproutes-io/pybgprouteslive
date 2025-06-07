from setuptools import setup, find_packages

setup(
    name='pybgprouteslive',
    version='0.1',
    description='Live BGP route processing client for Python',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'websocket-client',
        'requests',
    ],
    python_requires='>=3.7',
)

