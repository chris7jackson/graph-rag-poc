# Graph RAG Pipeline - Proof of Concept

A locally-executable Graph RAG (Retrieval-Augmented Generation) pipeline that constructs knowledge graphs from Wikipedia articles and enables LLM-powered querying.

## 🎯 Project Overview

This proof of concept demonstrates:
- **Knowledge Graph Construction**: Automated entity extraction and relationship mapping from Wikipedia articles
- **Multi-Model NER**: Combining GLiNER and spaCy for comprehensive entity recognition
- **Interactive Visualization**: Graph exploration through web-based interfaces
- **Intelligent Querying**: LLM-powered question answering using graph context

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

```python
# 1. Ingest Wikipedia articles
python -m src.ingestion.wikipedia --topics "Artificial Intelligence,Machine Learning" --max-articles 10

# 2. Extract entities and build graph
python -m src.extraction.pipeline --input data/articles --output data/graphs

# 3. Launch validation interface
streamlit run src/validation/app.py
# 4. Query the graph
python -m src.query.interface --question "What is machine learning?"
```

## 📁 Project Structure

```
graph-rag-poc/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── .env.example             # Environment variables template
│
├── src/                     # Source code
│   ├── __init__.py
│   ├── ingestion/           # Wikipedia data ingestion
│   │   ├── __init__.py
│   │   ├── wikipedia.py     # Wikipedia API wrapper
│   │   └── preprocessor.py  # Text cleaning
│   │
│   ├── extraction/          # Entity extraction pipeline
│   │   ├── __init__.py
│   │   ├── gliner_extractor.py  # GLiNER model
│   │   ├── spacy_extractor.py   # spaCy NER
│   │   └── pipeline.py          # Combined pipeline│   │
│   ├── graph/               # Graph construction
│   │   ├── __init__.py
│   │   ├── builder.py       # NetworkX graph builder
│   │   ├── relationships.py # Relationship extraction
│   │   └── visualizer.py    # PyVis visualization
│   │
│   ├── validation/          # Manual validation UI
│   │   ├── __init__.py
│   │   ├── app.py          # Streamlit application
│   │   └── operations.py   # Graph editing operations
│   │
│   └── query/              # LLM query interface
│       ├── __init__.py
│       ├── indexer.py      # ChromaDB indexing
│       ├── retriever.py    # Context retrieval
│       └── interface.py    # Query processing
│
├── data/                   # Data storage
│   ├── articles/          # Wikipedia articles (JSON)
│   ├── entities/          # Extracted entities (CSV)
│   ├── graphs/           # Graph files (pickle, graphml)
│   └── indexes/          # Vector indexes
│
├── notebooks/            # Jupyter notebooks
│   ├── 01_data_exploration.ipynb│   ├── 02_entity_extraction.ipynb
│   └── 03_graph_analysis.ipynb
│
├── configs/              # Configuration files
│   ├── pipeline.yaml    # Pipeline configuration
│   └── models.yaml      # Model settings
│
├── docs/                # Additional documentation
│   ├── ARCHITECTURE.md  # System architecture
│   ├── API.md          # API documentation
│   └── TROUBLESHOOTING.md
│
└── tests/              # Unit tests
    ├── test_ingestion.py
    ├── test_extraction.py
    └── test_graph.py
```

## 🔧 Features

### Current Features (PoC)
- ✅ Wikipedia article ingestion via API
- ✅ Entity extraction using GLiNER + spaCy
- ✅ Customizable entity types
- ✅ Co-occurrence based relationship extraction
- ✅ Interactive graph visualization
- ✅ Basic entity validation interface- ✅ Vector similarity search
- ✅ LLM-powered Q&A with graph context

### Planned Features (Production)
- 🔄 Real-time streaming pipeline
- 🔄 Advanced relationship extraction
- 🔄 Multi-source data ingestion
- 🔄 Collaborative validation
- 🔄 API endpoints
- 🔄 Production graph database (Neo4j)

## 🏗️ Architecture

The pipeline consists of five main stages:

1. **Data Ingestion**: Fetches and preprocesses Wikipedia articles
2. **Entity Extraction**: Multi-model NER using GLiNER and spaCy
3. **Graph Construction**: Builds NetworkX graph with entities and relationships
4. **Validation**: Manual review and correction through Streamlit UI
5. **Query Interface**: RAG-based Q&A using Ollama and ChromaDB

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## 📊 Configuration

### Pipeline Configuration (`configs/pipeline.yaml`)
```yaml
ingestion:  batch_size: 10
  cache_enabled: true
  output_format: json

extraction:
  models:
    gliner:
      model_name: "urchade/gliner_multi_pii-v1"
      confidence_threshold: 0.5
    spacy:
      model_name: "en_core_web_sm"
      enabled_components: ["ner", "parser"]
  
  entity_types:
    default: ["PERSON", "ORGANIZATION", "LOCATION"]
    custom: ["TECHNOLOGY", "CONCEPT", "EVENT"]

graph:
  backend: "networkx"
  max_nodes: 1000
  edge_weight_threshold: 0.3
  
llm:
  provider: "ollama"
  model: "phi3:mini"
  temperature: 0.3
  context_window: 4096
```
### Environment Variables (`.env`)
```bash
# Optional: Wikipedia API settings
WIKIPEDIA_LANG=en
WIKIPEDIA_USER_AGENT=GraphRAGPoC/1.0

# Ollama settings
OLLAMA_HOST=http://localhost:11434

# ChromaDB settings
CHROMA_PERSIST_DIR=./data/indexes/chroma

# Logging
LOG_LEVEL=INFO
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_extraction.py

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📈 Performance Metrics (PoC Targets)

| Metric | Target | Current ||--------|--------|---------|
| Articles processed | 10-20 | TBD |
| Entities extracted | 100+ | TBD |
| Graph nodes | 1000 | TBD |
| Query response time | <10s | TBD |
| Entity extraction F1 | >0.7 | TBD |

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
- NetworkX for graph manipulation- PyVis for visualization

## 📚 References

- [GLiNER: Generalist Model for Named Entity Recognition](https://github.com/urchade/GLiNER)
- [spaCy Documentation](https://spacy.io/)
- [NetworkX Documentation](https://networkx.org/)
- [Ollama Documentation](https://ollama.ai/)
- [ChromaDB Documentation](https://www.trychroma.com/)

## 🚧 Current Status

**Phase**: Proof of Concept  
**Timeline**: 6 weeks  
**Current Week**: 1 - Setup and Planning

### Development Phases
- [x] Week 0: Planning and architecture
- [ ] Week 1-2: Core pipeline development
- [ ] Week 3-4: Visualization and validation
- [ ] Week 5-6: LLM integration and testing

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---
*Last Updated: December 2024*