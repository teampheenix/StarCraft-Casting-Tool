"""Set up the sc2monitor via setuptools."""
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='StarCraftCastingTool',
      version='2.14.1',
      description=(''),
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/teampheenix/StarCraft-Casting-Tool',
      author='pressure',
      author_email='pres.sure@ymail.com',
      license='GPL-3.0',
      python_requires='>=3.8.0',
      tests_require=[
          'pytest >= 6.2.5',
          'pytest-mock >= 3.5.1',
          'pytest-qt >= 4.0.2'],
      packages=['scctool'],
      install_requires=[],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3.8'])
