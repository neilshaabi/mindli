venv:
	@echo "\nCreating virtual environment..."
	python3 -m venv .venv
	@echo "\nNote: You will need to activate the virtual environment in your shell manually using:"
	@echo "source .venv/bin/activate"

deps:
	@echo "\nInstalling dependencies..."
	pip install -r requirements.txt

app:
	@echo "\nRunning Flask app locally..."
	flask run

clean:
	@echo "\nCleaning up directory..."
	rm -rf .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

.PHONY: venv deps app clean