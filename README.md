![Fairyfly](https://raw.githubusercontent.com/ladybug-tools/artwork/refs/heads/master/icons_bugs/png/fairyflyborder.png)

[![Build Status](https://github.com/ladybug-tools/fairyfly-core/actions/workflows/ci.yaml/badge.svg)](https://github.com/ladybug-tools/fairyfly-core/actions)

[![Python 3.10](https://img.shields.io/badge/python-3.10-orange.svg)](https://www.python.org/downloads/release/python-3100/) [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/) [![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# fairyfly-core

Fairyfly is a collection of Python libraries to create representations of construction details
following [fairyfly-schema](https://github.com/ladybug-tools/fairyfly-schema/wiki).

This package is the core library that provides fairyfly's common functionalities.
To extend these functionalities you should install available Fairyfly extensions or write
your own.

Here are a number of frequently used extensions for Fairyfly:

- [fairyfly-therm](https://github.com/ladybug-tools/fairyfly-therm): Adds LBNL THERM simulation to Fairyfly.


# Installation

To install the core library use:

`pip install -U fairyfly-core`

To check if Fairyfly command line interface is installed correctly use `fairyfly viz` and you
should get a `viiiiiiiiiiiiizzzzzzzzz!` back in response! :bee:

# [API Documentation](https://www.ladybug.tools/fairyfly-core/docs/)

## Local Development
1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/fairyfly-core.git

# or

git clone https://github.com/ladybug-tools/fairyfly-core.git
```
2. Install dependencies:
```console
cd fairyfly-core
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest ./tests
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./fairyfly
sphinx-build -b html ./docs ./docs/_build/docs
```
