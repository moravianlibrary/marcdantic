PYTHON_BASE := python3.12
PYTHON_VENV := .venv
PYTHON := $(PYTHON_VENV)/bin/python
PYTHON_PIP := $(PYTHON_VENV)/bin/pip
PYTHON_DEPS := requirements.txt

.PHONY: generate_venv remove_venv regenerate_env

generate_venv:
	$(PYTHON_BASE) -m venv $(PYTHON_VENV)
	$(PYTHON) -m ensurepip  # Ensures pip is available
	$(PYTHON_PIP) install --upgrade pip
	$(PYTHON_PIP) install -r $(PYTHON_DEPS)

remove_venv:
	rm -rf $(PYTHON_VENV)

regenerate_env: remove_venv generate_venv

run:
	$(PYTHON) main.py

