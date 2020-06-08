# Get all python files tracked by git
ALL_LINT_FILES := $(shell python3 lint.py all)
DIFF_LINT_FILES := $(shell python3 lint.py diff)

lint:
	pylint $(ALL_LINT_FILES)

lint-diff:
	pylint $(DIFF_LINT_FILES)

test:
	python -m unittest
