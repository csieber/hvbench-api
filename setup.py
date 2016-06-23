try:
        from setuptools import setup
except ImportError:

        print("+++++++++++ WARNING +++++++++++")
        print("WARNING: setuptools not installed! This will break automatic installation of requirements!")
        print("Please install the Python packages python-etcd and arg manually.")
        print("+++++++++++++++++++++++++++++++++")
        from distutils.core import setup

setup(
    name="hvbench-api",

    version="0.1.0",

    author="Christian Sieber",
    author_email="c.sieber@tum.de",

    packages=["hvbenchapi"],

    scripts=['hvbench-ctrl', 'hvbench-log'],

    include_package_data=True,

    url="https://github.com/csieber/hvbench",

    license="LICENSE",

    description="Python API for hvbench.",

    long_description=open("README.md").read(),

    install_requires=[
        "python-etcd",
        "argh"
    ],
)
