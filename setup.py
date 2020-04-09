from setuptools import find_packages, setup

import covid_19

# TODO: Bind these requirements to specific versions to prevent them breaking something in the future.
INSTALL_REQUIREMENTS = [
    "bs4",
    "iPython",
    "pandas",
    "numpy",
    "matplotlib",
    "dropbox",
]

setup(
    name="Covid-19",  # TODO: Give the app a more descriptive name!
    packages=find_packages(),
    version=covid_19.__version__,
    install_requires=INSTALL_REQUIREMENTS,
    author="Giles Calder",
    author_email="gcalder94@protonmail.com",
    url="https://github.com/gcalder/COVID-19",
)
