from setuptools import find_packages, setup

short_description = "Application to provide restful API for transaction database"


def long_description() -> str:
    with open("README.md", "r") as f:
        return f.read()


def get_requirements() -> list[str]:
    """Setting the *install_requires* list to the lines of the *requirements.txt* is not advised
    unless the latter file's list of packages is minimal, i.e., containing only dependencies
    necessary for this package.
    """
    with open("requirements.txt", "r") as f:
        return f.read().splitlines()


setup(
    name="sbx-search",
    version="0.0.1.dev1",
    python_requires=">=3.8.6",
    project_urls={"Source": "", "Documentation": ""},
    description=short_description,
    long_description=long_description(),
    install_requires=get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Office/Business :: Financial",
        "Development Status :: 3 - Alpha",
    ],
    packages=find_packages(exclude=['docs', 'helm', 'static_data']),
    include_package_data=True,
    package_data={
        # If any package contains *.yaml files, include them
        "": ["*.yaml", "settings_default.ini", "py.typed"]
    },
)
