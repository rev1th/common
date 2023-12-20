
#This is what your ‘setup.py’ file should look like.
 
from setuptools import setup, find_packages
 
setup(
    name='common',
    version='1.0',
    packages = find_packages('src'),  # Automatically find the packages that are recognized in the '__init__.py'.
    package_dir={"": "src"}
)
