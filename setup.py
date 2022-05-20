#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

NAME = "cpacspy"
VERSION = "0.1.0"
AUTHOR = "Aidan Jungo"
EMAIL = "aidan.jungo@cfse.ch"
DESCRIPTION = "PyPI package to work with CPACS file and AeroMaps"
LONG_DESCRIPTION = "Python package to read, write and analyse CPACS AeroPerformanceMaps. You need to have TIXI and TIGL install on your computer to use this package."
URL = ""
REQUIRES_PYTHON = ">=3.7.0"
REQUIRED = []
README = "README.md"
PACKAGE_DIR = "src"
LICENSE = "Apache License 2.0"


setuptools.setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,
    include_package_data=True,
    package_dir={"": PACKAGE_DIR},
    license=LICENSE,
    packages=[NAME],
    python_requires=REQUIRES_PYTHON,
    keywords=["CPACS", "aircraft", "design", "xml", "aerodynamics", "coefficients", "databases"],
    install_requires=REQUIRED,
    # See: https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
