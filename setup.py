import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'Pyramid>=1.1a4',
    'pyramid-handlers',
    'velruse',
    'WebError',
    'celery',
    'colander', 'htmllaundry'
    ]

setup(name='tickee_api',
      version='0.0',
      description='tick.ee api server',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        ],
      author='Kevin Van Wilder',
      author_email='kevin@tick.ee',
      url='http://tick.ee',
      keywords='ticket generation',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = tickee_api:main
      """,
      )