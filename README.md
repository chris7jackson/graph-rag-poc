# Graph RAG Pipeline - Proof of Concept

A locally-executable Graph RAG (Retrieval-Augmented Generation) pipeline that constructs knowledge graphs from Wikipedia articles and enables interactive exploration and analysis.

## 🎯 Project Overview

This proof of concept demonstrates:
- **Knowledge Graph Construction**: Automated entity extraction and relationship mapping from Wikipedia articles
- **Multi-Model NER**: Combining GLiNER and spaCy for comprehensive entity recognition
- **Interactive Visualization**: Graph exploration through web-based interfaces
- **Real-time Validation**: Streamlit-based interface for graph exploration and analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- 8GB RAM minimum
- 10GB free disk space (for models)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/graph-rag-poc.git
cd graph-rag-poc
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. Install Ollama and download a model:
```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull phi3:mini
```

### Basic Usage

#### Option 1: Using Makefile (Recommended)
```bash
# Complete setup
make setup

# Run the complete pipeline
make run-pipeline

# Or run individual steps
make ingest
make extract
make build

# Launch validation interface
make validate

# Clean up generated files
make clean
```

**Available Commands:**
- `make setup` - Complete setup (install + models)
- `make run-pipeline` - Run complete pipeline
- `make ingest` - Ingest Wikipedia articles
- `make extract` - Extract entities
- `make build` - Build knowledge graph
- `make validate` - Launch validation interface
- `make clean` - Clean up generated files

#### Option 2: Direct Commands
```bash
# 1. Ingest Wikipedia articles
python -m src.ingestion.wikipedia --topics "Artificial Intelligence,Machine Learning" --max-articles 10

# 2. Extract entities and build graph
python -m src.extraction.pipeline --input data/articles --output data/graphs

# 3. Launch validation interface
streamlit run src/validation/app.py
```

### Interactive Demo

Run the Jupyter notebook for a step-by-step demonstration:
```bash
jupyter notebook notebooks/demo.ipynb
```

## 📁 Project Structure

```
graph-rag-poc/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
│
├── src/                     # Source code
│   ├── __init__.py
│   ├── ingestion/           # Wikipedia data ingestion
│   │   ├── __init__.py
│   │   └── wikipedia.py     # Wikipedia API wrapper
│   │
│   ├── extraction/          # Entity extraction pipeline
│   │   ├── __init__.py
│   │   ├── gliner_extractor.py  # GLiNER model
│   │   ├── spacy_extractor.py   # spaCy NER
│   │   └── pipeline.py          # Combined pipeline
│   │
│   ├── graph/               # Graph construction
│   │   ├── __init__.py
│   │   └── builder.py       # NetworkX graph builder
│   │
│   ├── validation/          # Interactive validation UI
│   │   ├── __init__.py
│   │   └── app.py          # Streamlit application
│   │
│   └── query/              # Query interface (planned)
│       └── __init__.py
│
├── data/                   # Data storage
│   ├── articles/          # Wikipedia articles (JSON)
│   ├── entities/          # Extracted entities (JSON)
│   └── graphs/           # Graph files (pickle, graphml, html)
│
├── notebooks/            # Jupyter notebooks
│   └── demo.ipynb       # Complete pipeline demonstration
│
├── configs/              # Configuration files
│   └── pipeline.yaml    # Pipeline configuration
│
├── docs/                # Additional documentation
│   └── ARCHITECTURE.md  # System architecture
│
└── tests/              # Unit tests
    └── test_ingestion.py
```

## 🔧 Features

### ✅ Current Features (Working)
- **Wikipedia Article Ingestion**: Robust article fetching with search fallback
- **Multi-Model Entity Extraction**: GLiNER + spaCy for comprehensive NER
- **Knowledge Graph Construction**: NetworkX-based graph with entities and relationships
- **Interactive Visualization**: PyVis-based HTML visualizations
- **Streamlit Validation Interface**: Web-based graph exploration and analysis
- **Graph Statistics**: Comprehensive metrics and entity analysis
- **Data Export**: GraphML and pickle formats for interoperability

### 🔄 Planned Features
- **LLM Query Interface**: Ollama-powered natural language querying
- **Advanced Relationship Extraction**: Beyond co-occurrence analysis
- **Multi-source Data Ingestion**: Support for other data sources
- **Production Database**: Neo4j integration for large-scale graphs
- **API Endpoints**: RESTful API for programmatic access

## 🏗️ Architecture

The pipeline consists of four main stages:

1. **Data Ingestion**: Fetches Wikipedia articles with intelligent search fallback
2. **Entity Extraction**: Multi-model NER using GLiNER and spaCy
3. **Graph Construction**: Builds NetworkX graph with entities and co-occurrence relationships
4. **Validation & Exploration**: Interactive Streamlit interface for graph analysis

## 📊 Current Performance

| Metric | Value | Status |
|--------|-------|--------|
| Articles processed | 4 | ✅ Working |
| Entities extracted | 481 | ✅ Working |
| Graph nodes | 481 | ✅ Working |
| Graph edges | 2,001 | ✅ Working |
| Entity types | 16 | ✅ Working |
| Connected components | 17 | ✅ Working |

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_ingestion.py

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📈 Usage Examples

### 1. Quick Start with Makefile
```bash
# Complete setup and run
make setup
make run-pipeline
make validate
```

### 2. Fetch Articles on AI Topics
```bash
python -m src.ingestion.wikipedia --topics "Deep Learning,Computer Vision,Natural Language Processing" --max-articles 5
```

### 3. Extract Entities and Build Graph
```bash
python -m src.extraction.pipeline --input data/articles --output data/graphs
```

### 4. Explore the Graph Interactively
```bash
streamlit run src/validation/app.py
```

### 5. Run the Complete Demo
```bash
jupyter notebook notebooks/demo.ipynb
```

## 🔍 Graph Analysis Features

The Streamlit validation interface provides:

- **Graph Overview**: Statistics, density, and entity distributions
- **Entity Management**: Search, filter, and analyze entities by type
- **Relationship Analysis**: Explore connections and relationship types
- **Interactive Visualization**: Generate custom graph visualizations
- **Data Export**: Download entities and relationships as CSV

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'spacy'"**
   ```bash
   make setup
   # or manually:
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **"Ollama port conflict"**
   ```bash
   ps aux | grep ollama
   kill -9 <PID>
   ollama serve
   ```

3. **"No articles found"**
   - Try different topic names
   - Check internet connection
   - Verify Wikipedia API access

4. **"make: command not found" (Windows)**
   - Install Make for Windows via Chocolatey: `choco install make`
   - Or use the direct commands instead of Makefile
   - Or use WSL (Windows Subsystem for Linux)

## 🤝 Contributing

This is a proof of concept project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- GLiNER team for zero-shot NER capabilities
- spaCy for robust NLP pipeline
- Ollama for local LLM deployment
- NetworkX for graph manipulation
- PyVis for interactive visualizations
- Streamlit for web interface framework

## 📚 References

- [GLiNER: Generalist Model for Named Entity Recognition](https://github.com/urchade/GLiNER)
- [spaCy Documentation](https://spacy.io/)
- [NetworkX Documentation](https://networkx.org/)
- [Ollama Documentation](https://ollama.ai/)
- [PyVis Documentation](https://pyvis.readthedocs.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🚧 Current Status

**Phase**: Proof of Concept ✅  
**Status**: Fully Functional  
**Last Updated**: August 2024

### ✅ Completed Features
- [x] Wikipedia article ingestion with search fallback
- [x] Multi-model entity extraction (GLiNER + spaCy)
- [x] Knowledge graph construction
- [x] Interactive Streamlit validation interface
- [x] Graph visualization and analysis
- [x] Comprehensive testing and error handling

### 🔄 Next Steps
- [ ] LLM query interface integration
- [ ] Advanced relationship extraction
- [ ] Multi-source data ingestion
- [ ] Production database integration

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---
*Last Updated: August 2024*