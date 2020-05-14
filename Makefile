# Get all python files tracked by git
ALL_LINT_FILES := $(shell git ls-files | grep '**.py' | xargs)
DIFF_LINT_FILES := $(shell git diff --name-only | grep '**.py' | xargs)

lint:
	pylint $(ALL_LINT_FILES)

lint-diff:
	pylint $(DIFF_LINT_FILES)
