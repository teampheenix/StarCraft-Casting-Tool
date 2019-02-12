"""Set up the sc2monitor via setuptools."""
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='StarCraftCastingTool',
      version='2.7.2',
      description=(''),
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/teampheenix/StarCraft-Casting-Tool',
      author='pressure',
      author_email='pres.sure@ymail.com',
      license='GPL-3.0',
      python_requires='>=3.6.0',
      tests_require=['pytest >= 4.2.0', 'pytest-qt >= 3.2.2'],
      packages=['scctool'],
      install_requires=[],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'])
