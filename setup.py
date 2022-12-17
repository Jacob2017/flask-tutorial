from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='0.1.0',
    packages=find_packages(),
    include_packages_data=True,
    install_requires=[
        'flask',
    ],
)