from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='Hermes-lnestelroad',
      version='1.0.2',
      url='https://github.com/lnestelroad/Hermes',
      license='GPLv3+',
      author='Liam Nestelroad',
      author_email='nestelroadliam@gmail.com',
      description='A python message bus architecture with zeromq',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      packages=find_packages(),
      install_requires=[
          'netifaces',
          'PyYAML',
          'pyzmq',
      ]
      )
