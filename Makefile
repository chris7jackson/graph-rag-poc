# Makefile for Graph RAG Pipeline

.PHONY: help install setup test clean run-pipeline validate ingest extract build

# Default target
help:
	@echo "Graph RAG Pipeline - Available Commands"
	@echo "======================================="
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Complete setup (install + models)"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean generated files"
	@echo "  make run-pipeline - Run complete pipeline"
	@echo "  make validate     - Launch validation UI"
	@echo "  make ingest       - Ingest Wikipedia articles"
	@echo "  make extract      - Extract entities"
	@echo "  make build        - Build knowledge graph"

# Installation
install:
	pip install -r requirements.txt

# Complete setup
setup: install
	python -m spacy download en_core_web_sm
	mkdir -p data/articles data/entities data/graphs data/indexes logs
	@echo "Setup complete!"

# Run tests
test:
	pytest tests/ -v

# Clean generated filesclean:
	rm -rf data/articles/*.json
	rm -rf data/entities/*.json
	rm -rf data/graphs/*
	rm -rf data/indexes/*
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete

# Pipeline operations
run-pipeline:
	python -m src.cli pipeline

ingest:
	python -m src.cli ingest

extract:
	python -m src.cli extract

build:
	python -m src.cli build --visualize

validate:
	streamlit run src/validation/app.py

# Development
dev:
	pip install -e .

# Formatting
format:
	black src/ tests/
	flake8 src/ tests/