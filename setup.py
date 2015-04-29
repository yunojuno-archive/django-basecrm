# -*- coding: utf-8 -*-
"""Setup file for basecrm library."""
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-basecrm",
    version="0.2.1",
    packages=[
        'django_basecrm',
    ],
    install_requires=['Django>=1.7', 'requests>=2.6'],
    include_package_data=True,
    description='A Django app that connects to the BaseCRM API (v2)',
    long_description=README,
    url='https://github.com/yunojuno/django-basecrm',
    author='Marcel Kornblum',
    author_email='marcel@yunojuno.com',
    maintainer='Hugo Rodger-Brown',
    maintainer_email='hugo@yunojuno.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
