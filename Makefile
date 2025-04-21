# Makefile for project maintenance tasks

.PHONY: docs

docs:
	pip install .[docs]
	pdoc machineconfig --output-dir docs
