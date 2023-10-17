import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the code version
version = {}
with open(os.path.join(here, "lionagi/version.py")) as fp:
    exec(fp.read(), version)
__version__ = version["__version__"]

install_requires = [
    "openai",
    "pandas",
    "python-dotenv",
    "requests",
    'beautifulsoup4'
]


setuptools.setup(
    name="lionagi",
    version=__version__,
    author="LionAGI",
    author_email="ocean@lionagi.ai",
    description="Towards Artificial General Intelligence",
    packages=setuptools.find_packages(include=["lionagi*"]),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
