#!/bin/sh

PYTHON_VENV=.venv
PYTHON=$PYTHON_VENV/bin/python

$PYTHON -m marcdantic "$@"
