RUNTEST=python -m unittest discover -v

.PHONY: test
test:
	${RUNTEST} test


