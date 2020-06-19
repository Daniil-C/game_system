#!/usr/bin/python3
from setuptools import setup, find_packages

setup(
    name="imaginarium",
    version="0.1",
    author="",
    author_email="",
    url="github.com/Daniil-C/game_system",
    description="Client for imaginarium game",
    packages=["imaginarium", "imaginarium.backend", "imaginarium.interface"],
    install_requires=["pygame", "wget"],
    include_package_data=True
)
