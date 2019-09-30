from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='flasql',
    version='0.0.2',
    description='Basic flask views to provide graphql endpoints',
    author='FarmLogs',
    packages=['flasql'],
    install_requires=requirements,
)
