from setuptools import setup, find_packages

setup(name='Hermes',
      version='0.1',
      url='https://github.com/lnestelroad/Hermes',
      license='MIT',
      author='Liam Nestelroad',
      author_email='nestelroadliam@gmail.com',
      description='A python message bus architecture with zeromq',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False)
