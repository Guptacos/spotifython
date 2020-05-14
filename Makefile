# Get all python files tracked by git
LINT_FILES := $(shell git ls-files | grep '**.py' | xargs)

lint:
	pylint $(LINT_FILES)
