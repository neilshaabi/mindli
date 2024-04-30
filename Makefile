help:
	@echo "Available commands: make [help, tree, venv, dependencies, requirements, app, celery, redis, migrate-db, reset-db, lint, test, clean]"

tree:
	tree -I 'node_modules|__pycache__|.venv'

venv:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "Note: You will need to activate the virtual environment in your shell manually using:"
	@echo "source .venv/bin/activate"

dependencies:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Node.js dependencies..."
	npm install

requirements:
	@echo "Updating requirements.txt..."
	pip freeze > requirements.txt

app:
	@echo "Building JavaScript assets..."
	npx webpack --mode development
	@echo "Running Flask app locally..."
	flask run

celery:
	@echo "Starting celery worker..."
	@echo "Note: requires connection with redis via redis-server"
	celery -A make_celery worker --loglevel INFO

redis:
	@echo "Starting redis server..."
	redis-server


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
	@echo "Formatting Python files..."
	black . --exclude '/(\.venv|migrations)/'
	@echo "Linting Python files..."
	flake8 --exclude .venv,./migrations
	@echo "Reorganising imports..."
	isort .

test:
	@echo "Running tests with pytest..."
	pytest -s -x

clean:
	@echo "Cleaning up directory..."
	rm -rf .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete
	rm -rf app/static/dist/*
	rm -rf node_modules
	@echo "Removed Python and JavaScript build files."

.PHONY: help venv dependencies requirements app celery redis migrate-db reset-db lint test clean