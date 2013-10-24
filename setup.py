try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme_file = "README.md"
license_file = "LICENSE"

with open(readme_file) as f:
    readme = f.read()

with open(license_file) as f:
    license = f.read()

setup(
    name='pyBGP',
    description='PyBGP',
    long_description=readme,
    author='Quentin Loos',
    author_email='contact@quentinloos.be',
    url='',
    version='0.1',
    packages=['pybgp'],
    license=license,
)
