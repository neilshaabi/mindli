venv:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "Note: You will need to activate the virtual environment in your shell manually using:"
	@echo "source .venv/bin/activate"

deps:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

app:
	@echo "Running Flask app locally..."
	flask run

clean:
	@echo "Cleaning up directory..."
	rm -rf .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

lint:
	@echo "Reorganising imports..."
	isort .
	@echo "Formatting Python files..."
	black . --exclude '/(\.venv|migrations)/'
	@echo "Linting Python files..."
	flake8 --exclude .venv,./migrations

test:
	@echo "Running tests with pytest..."
	pytest -s

help:
	@echo "Available commands: make [help, venv, deps, app, test, clean]"

.PHONY: help venv deps app lint test clean