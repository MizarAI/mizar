from pathlib import Path

from setuptools import find_packages
from setuptools import setup

__version__ = "0.1.3"

ROOT_DIR = Path(".")

with open("requirements.txt") as f:
    requirements = f.readlines()

with open(str(ROOT_DIR / "README.md")) as readme:
    long_description = readme.read()

setup(
    name="mizar",
    version=__version__,
    author="MizarAI",
    author_email="info@mizar.ai",
    description="Official API for the MizarAI platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MizarAI/mizar",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=requirements,
    project_urls={
        "Bug Tracker": "https://github.com/MizarAI/mizar/issues",
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Office/Business",
        "Topic :: System :: Networking",
        "Topic :: Communications :: Chat",
        "Intended Audience :: Developers",
    ],
)
