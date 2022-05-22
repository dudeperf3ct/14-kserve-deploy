from setuptools import find_packages, setup

setup(
    name="sentiment",
    version="0.1.0",
    packages=find_packages(include=["sentiment", "sentiment.*"]),
)
