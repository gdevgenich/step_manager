#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name="step_manager",
    author="Vitold Sedyshev, Dmitry Girdyuk",
    author_email="vit1251@gmail.com",
    keywords="test mnager",
    version="1.19",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False
)
