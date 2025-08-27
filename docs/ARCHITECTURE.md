# System Architecture Documentation

## Overview

The Graph RAG Pipeline is a modular, locally-executable system that transforms unstructured Wikipedia text into an interactive knowledge graph for exploration and analysis. The system is currently in a fully functional proof-of-concept state.

## Architecture Principles

1. **Modularity**: Each component is independently testable and replaceable
2. **Local-First**: All processing occurs locally without external API dependencies (except Wikipedia)
3. **Incremental Processing**: Support for batch data processing
4. **Extensibility**: Easy addition of new entity types and extractors

## System Components

### 1. Data Layer

```
┌─────────────────────────────────────────┐
│           Wikipedia API                  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│        Ingestion Module                  │
│  - Rate limiting                         │
│  - Content extraction                    │
│  - Search fallback                       │
│  - Metadata preservation                 │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│      Local Storage (JSON)                │
└─────────────────────────────────────────┘
```
**Key Technologies:**
- `wikipedia`: Python wrapper for Wikipedia API
- JSON for intermediate storage
- Intelligent search fallback for inexact titles

### 2. Extraction Layer

```
┌─────────────────────────────────────────┐
│         Text Preprocessing               │
│  - Sentence segmentation                 │
│  - Tokenization                          │
│  - Cleaning                              │
└────────────┬────────────────────────────┘
             │
             ├──────────────┬──────────────┐
             ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   GLiNER     │ │    spaCy     │ │   Combined   │
│  Zero-shot   │ │  Pre-trained │ │   Pipeline   │
│     NER      │ │     NER      │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────┐
│         Entity Resolution                │
│  - Deduplication                         │
│  - Confidence scoring                    │
└─────────────────────────────────────────┘
```

**Entity Extraction Pipeline:**

1. **GLiNER** (Generalist Model):
   - Zero-shot learning for custom entity types
   - No retraining required for new labels
   - Confidence threshold: 0.5 (configurable)

2. **spaCy** (Traditional NER):
   - Fast, reliable extraction for standard entities
   - Pre-trained on large corpora
   - Provides dependency parsing for relationships

3. **Combined Strategy**:
   - Union of entities from both models
   - Confidence-weighted deduplication
   - Comprehensive entity coverage

### 3. Graph Construction Layer

```
┌─────────────────────────────────────────┐
│         Entity Nodes                     │
│  - ID, Label, Value                      │
│  - Confidence, Source                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│      Relationship Extraction             │
│  - Co-occurrence (same sentence)         │
│  - Weighted connections                  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│         NetworkX Graph                   │
│  - Directed multigraph                   │
│  - Weighted edges                        │
│  - Node/edge attributes                  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│        Persistence Layer                 │
│  - Pickle (fast save/load)               │
│  - GraphML (interoperability)            │
│  - HTML (interactive visualization)      │
└─────────────────────────────────────────┘
```

**Graph Schema:**

```python
# Node structure
node = {
    'id': 'unique_identifier',
    'text': 'Entity text',
    'label': 'PERSON|ORG|LOCATION|...',
    'confidence': 0.0-1.0,
    'count': 1,
    'sources': ['article_id1', 'article_id2']
}

# Edge structure
edge = {
    'source': 'node_id1',
    'target': 'node_id2',
    'type': 'RELATED_TO',
    'weight': 0.0-1.0,
    'count': 1
}
```

### 4. Validation & Exploration Layer

```
┌─────────────────────────────────────────┐
│         Streamlit Web UI                 │
│  ┌────────────────────────────────────┐ │
│  │     Graph Overview                 │ │
│  │  - Statistics & metrics            │ │
│  │  - Entity type distribution        │ │
│  │  - Top entities by centrality      │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │      Entity Management             │ │
│  │  - Search & filter                 │ │
│  │  - Entity analysis                 │ │
│  │  - Data export                     │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │     Relationship Analysis          │ │
│  │  - Top relationships               │ │
│  │  - Relationship statistics         │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │     Interactive Visualization      │ │
│  │  - PyVis network graphs            │ │
│  │  - Customizable layouts            │ │
│  │  - Node filtering                  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Data Flow

### 1. Ingestion Flow
```
Wikipedia API → Article JSON → Text Preprocessing → Clean Text
```

### 2. Extraction Flow
```
Clean Text → NER Models → Raw Entities → Resolution → Clean Entities
```

### 3. Graph Construction Flow
```
Clean Entities → Node Creation → Relationship Extraction → Graph Building → Persistence
```

### 4. Exploration Flow
```
Graph Data → Streamlit Interface → Interactive Analysis → Data Export
```

### 5. Query Flow (Planned)
```
User Query → Entity Recognition → Graph Retrieval → Context Building → Ollama LLM → Response
```

## Technology Stack Details

### Core Dependencies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.9+ | Core implementation |
| NER (Zero-shot) | GLiNER | Latest | Custom entity extraction |
| NER (Traditional) | spaCy | 3.7+ | Standard entity extraction |
| Graph Engine | NetworkX | 3.1+ | Graph manipulation |
| Visualization | PyVis | 0.3+ | Interactive graphs |
| Web UI | Streamlit | 1.28+ | Validation interface |
| File Monitoring | Watchdog | 6.0+ | Streamlit performance optimization |
| Data Processing | Pandas | 2.0+ | Data manipulation |
| Wikipedia API | wikipedia | Latest | Article fetching |
| LLM Runtime | Ollama | Latest | Local LLM hosting |

### Model Specifications

#### NER Models
- **GLiNER**: `urchade/gliner_multi_pii-v1` (50MB)
- **spaCy**: `en_core_web_sm` (12MB)

#### LLM Models (via Ollama)
- **Primary**: Phi-3 Mini (2.3GB) - Currently deployed and tested
- **Alternative**: Mistral 7B (4.1GB)
- **Fallback**: Llama 2 7B (3.8GB)

## Performance Characteristics

### Current Performance Metrics

| Operation | Actual Performance | Status |
|-----------|-------------------|--------|
| Article ingestion | 2-5 sec/article | ✅ Working |
| Entity extraction | 10-15 sec/article | ✅ Working |
| Graph construction | <1 sec/100 entities | ✅ Working |
| Visualization render | <2 seconds | ✅ Working |
| Streamlit interface | <1 second load | ✅ Working |
| File monitoring | Real-time updates | ✅ Working |

### Resource Requirements

- **Memory**: 4-8GB RAM (depending on graph size)
- **Storage**: 5GB (models + data)
- **CPU**: 4+ cores recommended
- **GPU**: Optional (speeds up embedding generation)

## Current System Capabilities

### ✅ Implemented Features

1. **Wikipedia Article Ingestion**
   - Robust article fetching with search fallback
   - Command-line interface with topic specification
   - JSON storage with metadata preservation

2. **Multi-Model Entity Extraction**
   - GLiNER for zero-shot entity recognition
   - spaCy for traditional NER
   - Combined pipeline for comprehensive coverage
   - Confidence scoring and deduplication

3. **Knowledge Graph Construction**
   - NetworkX-based graph with entities and relationships
   - Co-occurrence-based relationship extraction
   - Weighted edges and node attributes
   - Multiple export formats (Pickle, GraphML, HTML)

4. **Interactive Validation Interface**
   - Streamlit-based web application
   - Graph statistics and entity analysis
   - Search and filtering capabilities
   - Interactive PyVis visualizations
   - Data export functionality

### 🔄 Planned Features

1. **LLM Query Interface**
   - Ollama integration for natural language queries
   - Graph-aware context retrieval
   - RAG-based question answering
   - Query understanding and entity extraction
   - Context assembly from graph traversal

2. **Advanced Graph Features**
   - Neo4j database integration
   - Advanced relationship extraction
   - Graph neural networks

3. **Production Features**
   - REST API endpoints
   - Docker containerization
   - Distributed processing

## Error Handling Strategy

### Current Error Handling
1. **Wikipedia API Failures**: Search fallback for inexact titles
2. **NER Model Failures**: Graceful degradation to single model
3. **Memory Issues**: Graph size limits and pruning
4. **File I/O Errors**: Comprehensive error logging and recovery
5. **Ollama Service Issues**: Port conflict resolution and service management

### Error Recovery
- Automatic retry for transient failures
- Comprehensive error logging
- Graceful degradation for non-critical failures

## Monitoring & Observability

### Current Metrics
- Entity extraction counts and types
- Graph size and complexity metrics
- Processing times for each pipeline stage
- Memory usage during processing

### Logging Strategy
```python
# Structured logging format
{
    "timestamp": "2024-08-27T12:00:00Z",
    "level": "INFO",
    "component": "extraction",
    "event": "entities_extracted",
    "data": {
        "article_id": "123",
        "entity_count": 42,
        "duration_ms": 1234
    }
}
```

## Development Workflow

### Local Development
1. Set up virtual environment
2. Install dependencies
3. Download spaCy model
4. Run tests
5. Start Streamlit app

### Testing Strategy
- Unit tests for each module
- Integration tests for pipelines
- End-to-end tests with sample data

## Configuration Management

### Current Configuration
- Pipeline settings in `configs/pipeline.yaml`
- Model parameters in code
- Command-line arguments for user input

### Configuration Hierarchy
1. Default values in code
2. Configuration files
3. Command-line arguments

## Current Limitations

### PoC Limitations
- Single-threaded processing
- In-memory graph storage
- Limited to ~1000 nodes for optimal performance
- No distributed processing
- No persistent graph database

### Known Issues
- GraphML export requires data type conversion
- Large graphs may impact Streamlit performance
- No incremental graph updates

## Future Enhancements

### Short-term (3 months)
- [ ] LLM query interface with Ollama
- [ ] Advanced relationship extraction
- [ ] Graph database integration (Neo4j)
- [ ] Multi-threading for extraction

### Medium-term (6 months)
- [ ] REST API implementation
- [ ] Docker containerization
- [ ] Real-time streaming pipeline
- [ ] Advanced visualization features

### Long-term (12 months)
- [ ] Distributed processing
- [ ] Active learning for NER
- [ ] Graph neural networks
- [ ] Production deployment

## Appendix: Key Design Decisions

### Why NetworkX for PoC?
- Pure Python, no external dependencies
- Rich graph algorithms library
- Easy serialization
- Good enough for <10K nodes

### Why GLiNER + spaCy?
- GLiNER: Zero-shot learning for custom entities
- spaCy: Fast, reliable for standard entities
- Combined: Best of both worlds

### Why Streamlit?
- Rapid prototyping
- Built-in components for data apps
- No frontend development needed
- Excellent for data exploration
- Watchdog integration for performance optimization

### Why PyVis?
- Interactive network visualizations
- Easy integration with NetworkX
- Customizable styling and layouts
- HTML export for sharing

### Why Ollama?
- Truly local LLM execution
- Simple API and model management
- Good model selection (phi3:mini, Mistral, Llama)
- No external API dependencies

## Current Status

**Phase**: Proof of Concept ✅  
**Status**: Fully Functional  
**Last Updated**: August 2024  
**Version**: 1.0 (Working PoC)

### Success Metrics Achieved
- ✅ 481 entities extracted from 4 articles
- ✅ 2,001 relationships established
- ✅ Interactive visualization working
- ✅ Streamlit interface functional
- ✅ End-to-end pipeline operational
- ✅ Ollama service running with phi3:mini model

---
*Last Updated: August 2024*  
*Version: 1.0 (Working PoC)*