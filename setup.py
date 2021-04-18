from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('version.txt', 'r', encoding='utf-8') as vf:
    hermes_version = vf.read()

setup(name='Hermes-lnestelroad',
      version=hermes_version,
      url='https://github.com/lnestelroad/Hermes',
      license='GPLv3+',
      author='Liam Nestelroad',
      author_email='nestelroadliam@gmail.com',
      description='A python message bus architecture with zeromq',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Operating System :: MacOS :: MacOS X"
      ],
      packages=find_packages(),
      install_requires=[
          'netifaces',
          'PyYAML',
          'pyzmq',
      ],
      entry_points={
          'console_scripts': [
              'hermes = Hermes.main:main'
          ]
      },
      )
