#!/usr/bin/env python
"""
Quick start script for Graph RAG Pipeline

This script sets up the environment and runs a simple demo.
"""

import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")


def install_dependencies():
    """Install required packages."""
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✓ Dependencies installed")


def download_spacy_model():
    """Download spaCy model."""
    print("\n📥 Downloading spaCy model...")
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    print("✓ spaCy model downloaded")

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directory structure...")
    dirs = [
        "data/articles",
        "data/entities",
        "data/graphs",
        "data/indexes",
        "data/cache",
        "logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created")


def check_ollama():
    """Check if Ollama is installed."""
    print("\n🤖 Checking Ollama installation...")
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama is installed")
            print("  To use LLM features, make sure to:")
            print("  1. Start Ollama: ollama serve")
            print("  2. Pull a model: ollama pull phi3:mini")
        else:
            raise FileNotFoundError    except FileNotFoundError:
        print("⚠️  Ollama not found")
        print("  To enable LLM features, install Ollama:")
        print("  macOS: brew install ollama")
        print("  Linux: curl -fsSL https://ollama.ai/install.sh | sh")


def run_demo():
    """Run a simple demo."""
    print("\n🚀 Running demo pipeline...")
    print("=" * 50)
    
    # Run the pipeline
    subprocess.run([sys.executable, "-m", "src.cli", "pipeline"])


def main():
    """Main function."""
    print("=" * 50)
    print("Graph RAG Pipeline - Quick Start")
    print("=" * 50)
    
    # Check environment
    check_python_version()
    
    # Setup
    print("\n🔧 Setting up environment...")
    install_dependencies()
    download_spacy_model()
    create_directories()
    check_ollama()
    
    print("\n✅ Setup complete!")    
    # Ask user if they want to run demo
    print("\n" + "=" * 50)
    response = input("Would you like to run a demo? (y/n): ")
    
    if response.lower() == 'y':
        run_demo()
        
        print("\n" + "=" * 50)
        print("Demo complete! You can now:")
        print("1. View the graph: open data/graphs/graph.html")
        print("2. Launch validation UI: streamlit run src/validation/app.py")
        print("3. Explore the notebook: jupyter notebook notebooks/demo.ipynb")
    else:
        print("\n" + "=" * 50)
        print("Setup complete! Available commands:")
        print("  • Ingest: python -m src.cli ingest --help")
        print("  • Extract: python -m src.cli extract --help")
        print("  • Build: python -m src.cli build --help")
        print("  • Validate: python -m src.cli validate")
        print("  • Full pipeline: python -m src.cli pipeline")
    
    print("\nFor more information, see README.md")
    print("=" * 50)


if __name__ == "__main__":
    main()