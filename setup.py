from setuptools import find_packages
from setuptools import setup

setup(
    name="Mizar",
    version="0.1.0",
    author="The Mizar Team",
    author_email="jack@mizar.ai",
    description="Mizar is a library to interact with mizar.ai",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points="""
    [console_scripts]
    mizar=mizar.cli:cli
    """,
    install_requires=[
        "click>=5.1",
        "requests==2.23.0",
        "scikit-learn>=0.22.2",
        "pandas>=1.0.1",
    ],
    classifiers="Programming Language :: Python :: 3.6",
)
