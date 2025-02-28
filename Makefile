SRCPATH :=  $(CURDIR)
PROJECTNAME := $(shell basename $(CURDIR))
TOPTARGET := help
GITCURBRANCH := $(shell git rev-parse --abrev-ref HEAD)
SUBDIRS := $(wildcard */.)

define HELP
Manage $(PROJECTNAME).
Usage:

make docs           - make sphinx doc

make build          - build project
make publish        - publish to pypi
make clean          - clean project

make coverage       - pytest coverage (WIP)

make git_tag_TAG    - git tag TAG
endef
export HELP

# .PHONY: target_1 target_...
.PHONY: docs clean build publish coverage

.PHONY: help
help:
	@echo "$$HELP"

# sphinx-build --color -T -a -n  -E -c debug debug/_src debug/_build
# sphinx-build -j 8 -W -c debug debug/_src debug/_build
.PHONY: docs
docs:
	@poetry run sphinx-build --color -T -a -n -E -c docs docs docs/_build


# .PHONY: git_tag_%
git_tag_%:
	@$(if $(shell ./check_semver.py ${*} 2>/dev/null),, $(error Invalid tag: ${*}))
	@echo "Tag: ${*}"
	@cp pyproject.toml pyproject.toml.old
	@sed -e "s~^\(version.*[\"]\)\(.*\)\([\"]\).*$$~\1${*}\3~" < pyproject.toml.old > pyproject.toml
	@(git commit -m "Tag: ${*}"  pyproject.toml  && git tag ${*} && git push --follow-tags && git push --tags) \
		|| mv pyproject.toml.old pyproject.toml \
		&& rm pyproject.toml.old


.PHONY: clean
clean:
	@rm -rf dist .coverage coverage.xml
	@rm -rf docs/_build docs/apidocs
	@find . -name __pycache__ -type d -print0 | xargs -0 rm -rf
	@find docs/demos -name _\* -type d -print0 | xargs -0 rm -rf


.PHONY: build
build:
	@rm -rf dist
	@poetry build
	@twine check dist/*

.PHONY: publish
publish: clean build
	@poetry publish


.PHONY: coverage
coverage:
	@pytest --cov=sphinx_autopages --cov-report=xml --cov-report=term-missing


