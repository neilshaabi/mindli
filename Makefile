help:
	@echo "Available commands: make [help, venv, deps, app, migrate-db, reset-db, lint, test, clean]"

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

migrate-db:
	@echo "Generating database migrations..."
	flask db migrate
	@echo "Applying database migrations..."
	flask db upgrade

reset-db:
	@echo "Resetting the database..."
	flask db downgrade
	flask db upgrade

lint:
	@echo "Reorganising imports..."
	isort .
	@echo "Formatting Python files..."
	black . --exclude '/(\.venv|migrations)/'
	@echo "Linting Python files..."
	flake8 --exclude .venv,./migrations

test:
	@echo "Running tests with pytest..."
	pytest -s -x

clean:
	@echo "Cleaning up directory..."
	rm -rf .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

.PHONY: help venv deps app migrate-db reset-db lint test clean