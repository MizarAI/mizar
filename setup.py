from pathlib import Path

from setuptools import find_packages
from setuptools import setup

__version__ = "0.1.0"

ROOT_DIR = Path(".")

with open(str(ROOT_DIR / "README.md")) as readme:
    long_description = readme.read()

setup(
    name="Mizar",
    version=__version__,
    author="mizar.ai",
    author_email="jack@mizar.ai, francesco@mizar.ai, alex@mizar.ai",
    description="Official API for the mizar.ai platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MizarAI/mizar",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "click>=5.1",
        "requests==2.23.0",
        "scikit-learn>=0.22.2",
        "pandas>=1.0.1",
        "requests"
    ],
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
    ]
)
