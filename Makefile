SHELL := /bin/bash

FILES := \
	.

# Python
PYTHON := python
ifneq ($(wildcard ./.venv/bin/python),)
	PYTHON := ./.venv/bin/python
endif
ifneq ($(wildcard ./venv/bin/python),)
	PYTHON := ./venv/bin/python
endif

pretty:
	$(PYTHON) -m ruff format $(FILES)

check:
	$(PYTHON) -m ruff check $(FILES)

all: pretty check