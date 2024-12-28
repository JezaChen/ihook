from setuptools import find_packages, setup


def get_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="ihook",
    version="0.1.1",
    url="https://github.com/JezaChen/ihook",
    author="Jianzhang Chen",
    author_email="jezachen@163.com",
    license="MIT",
    description="`ihook` is a Python module that allows you to configure functions to call when importing modules.",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("*examples", "*examples.*", "*tests", "*tests.*")),
    python_requires=">=3.7, <4",
    keywords="hook import importlib",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
    ],
)
