SHELL = /usr/bin/env bash -o pipefail

default: help

.PHONY .SILENT: help
help:
	# Usage:
	@sed -n '/^\([a-z][^:]*\).*/s//    make \1/p' $(MAKEFILE_LIST)

.PHONY .SILENT: install
install:
	poetry env use 3.10; \
	poetry install; \
	for directory in components/* applications/*; do \
	    echo $$directory; \
		pushd $$directory > /dev/null; \
		poetry install; \
		popd > /dev/null; \
	done

.PHONY .SILENT: test
test:
	for directory in components/* applications/*; do \
		pushd $$directory > /dev/null; \
		if [ -d tests ]; then \
			echo "running tests in $$directory"; \
	    	poetry run mypy --strict `basename $$directory` tests; \
			poetry run python -m unittest; \
		fi; \
		popd > /dev/null; \
	done

.PHONY .SILENT: check
check:
	poetry run black --check .; \
	poetry run flake8 .;

.PHONY .SILENT: format
format:
	poetry run black .;

.PHONY .SILENT: run
run:
	source .env; \
	pushd applications/starter_app > /dev/null; \
    poetry run python -m starter_app; \
	popd > /dev/null;
