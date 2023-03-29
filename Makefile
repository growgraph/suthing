RUNTEST=python -m unittest discover -v

.PHONY: test
test:
	${RUNTEST} test

.PHONY: black
black:
	find suthing test -name "*py"| xargs black -l 79 --preview

.PHONY: mypy
mypy:
	mypy suthing

.PHONY: isort
isort:
	find suthing test -name "*py" | xargs isort --line-length=79


all: black isort mypy


