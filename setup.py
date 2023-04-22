import nagerapi, os

from setuptools import setup, find_packages

with open("README.rst", "r") as f:
    long_descr = f.read()
long_descr = long_descr.replace(":class:", "")

__version__ = None
if os.path.exists("VERSION"):
    with open("VERSION") as handle:
        for line in handle.readlines():
            line = line.strip()
            if len(line) > 0:
                __version__ = line
                break

setup(
    name=nagerapi.__package_name__,
    version=__version__,
    description=nagerapi.__description__,
    long_description=long_descr,
    url=nagerapi.__url__,
    author=nagerapi.__author__,
    author_email=nagerapi.__email__,
    license=nagerapi.__license__,
    packages=find_packages(),
    python_requires=">=3.6",
    keywords=["nagerapi", "nager", "wrapper", "api"],
    install_requires=[
        "requests"
    ],
    project_urls={
        "Documentation": "https://nagerapi.metamanager.wiki",
        "Funding": "https://github.com/sponsors/meisnate12",
        "Source": "https://github.com/meisnate12/NagerAPI",
        "Issues": "https://github.com/meisnate12/NagerAPI/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ]
)
