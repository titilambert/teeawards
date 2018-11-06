#!/usr/bin/env python3
import os

from setuptools import setup
from setuptools import setup, find_packages

def package_files(dest, directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return (dest, paths)


PACKAGES = find_packages(exclude=['tests', 'tests.*'])


setup(name='teeawards',
      version='0.1.0',
      description='',
      author='',
      author_email='',
      url='https://github.com/titilambert/teeawards',
      package_data={'': ['LICENSE', 'requirements.txt', 'test_requirements.txt'],
                    },
#      data_files=DATA_FILES,
#      include_package_data=True,
      packages=PACKAGES,
      entry_points={
          'console_scripts': [
              'teeawards = teeawards.__main__:main'
          ]
      },
      license='',
      zip_safe=False,
      platforms='any',
      install_requires=[
                        "pymongo",
                        "influxdb",
                        "Mako",
                        "hug",
                        ],
      classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
)
