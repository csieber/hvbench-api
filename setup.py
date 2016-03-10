from distutils.core import setup

setup(
    name="HVBench-API",

    version="0.1.0",

    author="Christian Sieber",
    author_email="c.sieber@tum.de",

    packages=["hvbenchapi"],

    include_package_data=True,

    url="http://pypi.python.org/pypi/MyApplication_v010/",

    license="LICENSE.txt",

    description="HVBench-API.",

    long_description=open("README.txt").read(),

    install_requires=[
        "python-etc",
    ],
)
