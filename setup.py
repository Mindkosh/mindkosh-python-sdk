# Copyright (C) 2022 Mindkosh Technologies. All rights reserved.
# Author: Shikhar Dev Gupta                                         

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mindkosh',
    version='1.1',
    description="Mindkosh Python SDK",
    long_description=long_description,
    url='https://mindkosh.com',
    author="Mindkosh",
    author_email="support@labelbox.com",
    packages=find_packages(),
    install_requires=[
        "Pillow>=6.2.0",
        "requests>=2.20.1",
        "requests-toolbelt==0.9.1",
        "shortuuid==1.0.8"
    ],
    include_package_data=True,
    python_requires='>=3.7',
    keywords=["mindkosh"],
)