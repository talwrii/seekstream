import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "seekstream",
    version = "0.1",
    author = "Tal Wrii",
    author_email = "talwrii@gmail.com",
    description = ("Render an unseekable stream seekable"
                   " by in memory caching"),
    license = "BSD",
    keywords = "seek stream file",
    url = "https://github.com/talwrii/seekstream",
    py_modules = ['seekstream'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
)
