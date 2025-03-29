# Copyright (C) 2024 Mindkosh Technologies. All rights reserved.
# Author: Shikhar Dev Gupta

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mindkosh',
    version='1.0.1',
    description="Mindkosh Python SDK",
    long_description=long_description,
    url='https://github.com/Mindkosh/mindkosh-python-sdk',
    author="Mindkosh",
    author_email="shikhar@mindkosh.com",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        "requests>=2.20.1",
        "Pillow==9.2.0",
        "matplotlib==3.5.1",
        "datumaro==0.3.1",
        "requests-toolbelt==0.10.1",
        "appengine-python-standard==1.1.2",
        "alive-progress==2.4.1",
        "validators==0.20.0",
        "mplcursors==0.5.1",
        "python-dotenv==0.21.0",
        "aiohttp==3.8.3"
    ],
    keywords=[
        "annotation",
        "segmentation",
        "pointcloud",
        "computervision",],
)