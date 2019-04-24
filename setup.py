#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name="step_manager",
    author="Vitold Sedyshev, Dmitry Girdyuk",
    author_email="vit1251@gmail.com",
    keywords="step manager",
    version="2.10",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False
)
