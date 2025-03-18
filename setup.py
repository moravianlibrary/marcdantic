from setuptools import setup, find_packages


def read_description():
    with open("description.txt") as f:
        return f.read()


def read_long_description():
    with open("README.md") as f:
        return f.read()


def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def read_version():
    with open("VERSION", "r") as version_file:
        return version_file.read().strip()


setup(
    name="marcdantic",
    version=read_version(),
    description=read_description(),
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="Robert Randiak",
    author_email="randiak@protonmail.com",
    packages=find_packages(),
    install_requires=read_requirements(),
    setup_requires=["wheel"],
    python_requires=">=3.8",
)
