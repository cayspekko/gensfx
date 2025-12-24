.PHONY: install run test clean help

help:
	@echo "SoundForge - Makefile commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the Streamlit app"
	@echo "  make test       - Run tests with pytest"
	@echo "  make clean      - Clean generated files"

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
