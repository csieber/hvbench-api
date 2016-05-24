from distutils.core import setup

setup(
    name="hvbench-api",

    version="0.1.0",

    author="Christian Sieber",
    author_email="c.sieber@tum.de",

    packages=["hvbenchapi"],

    scripts=['hvbench-ctrl'],

    include_package_data=True,

    url="http://pypi.python.org/pypi/MyApplication_v010/",

    license="LICENSE",

    description="Python API for hvbench.",

    long_description=open("README.md").read(),

    install_requires=[
        "python-etc",
        "argh"
    ],
)
