.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
PY_PATH := "$(shell python -c 'import sys; print(sys.prefix)')"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 babelizer tests

pretty: ## reformat files to make them look pretty
	isort babelizer tests
	black setup.py babelizer tests docs/source/conf.py --exclude=babelizer/data

test: ## run tests quickly with the default Python
	pytest tests --disable-warnings -vvv

test-languages: ## run tests on babelizer languages
	pytest external/tests --disable-warnings -vvv

coverage: ## check code coverage quickly with the default Python
	coverage run --source babelizer --omit */babelizer/data/* -m pytest tests external/tests
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	sphinx-apidoc -o docs/source/api babelizer --separate
	rm -f docs/source/api/babelizer.rst
	rm -f docs/source/api/modules.rst
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

test-release: dist ## package and upload a release to TestPyPI
	twine upload --repository testpypi dist/*

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python -m build
	ls -l dist
	twine check dist/*

install: clean ## install the package to the active Python's site-packages
	pip install -e .

joss: ## make the paper
	docker run --rm \
    --volume $(shell pwd)/paper:/data \
    --user $(shell id -u):$(shell id -g) \
    --env JOURNAL=joss \
    openjournals/paperdraft
	open paper/paper.pdf

examples: c-example cxx-example fortran-example python-example ## build the language examples

c-example:
	cmake -S external/bmi-example-c -B external/build/c -DCMAKE_INSTALL_PREFIX=$(PY_PATH)
	make -C external/build/c install

cxx-example:
	cmake -S external/bmi-example-cxx -B external/build/cxx -DCMAKE_INSTALL_PREFIX=$(PY_PATH)
	make -C external/build/cxx install

fortran-example:
	export
	cmake -S external/bmi-example-fortran -B external/build/fortran -DCMAKE_INSTALL_PREFIX=$(PY_PATH)
	make -C external/build/fortran install

python-example:
	make -C external/bmi-example-python install
