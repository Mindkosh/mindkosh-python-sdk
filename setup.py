# Copyright (C) 2024 Mindkosh Technologies. All rights reserved.
# Author: Shikhar Dev Gupta

from setuptools import setup, find_packages

def get_long_description():
    with open("README.md", "r") as fh:
        return fh.read()

def get_requirements():
    requirements = []
    with open('requirements.txt') as lines:
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements

setup(
    name='mindkosh',
    version='1.0.2',
    description="Mindkosh Python SDK",
    long_description=get_long_description(),
    url='https://github.com/Mindkosh/mindkosh-python-sdk',
    author="Mindkosh",
    author_email="shikhar@mindkosh.com",
    packages=find_packages(),
    include_package_data=True,
    license="Apache-2.0",
    python_requires='>=3.7',
    install_requires=get_requirements(),
    keywords=[
        "annotation",
        "segmentation",
        "pointcloud",
        "computervision",],
)