# System Architecture Documentation

## Overview

The Graph RAG Pipeline is designed as a modular, locally-executable system that transforms unstructured Wikipedia text into a queryable knowledge graph enhanced with LLM capabilities.

## Architecture Principles

1. **Modularity**: Each component is independently testable and replaceable
2. **Local-First**: All processing occurs locally without external API dependencies (except Wikipedia)
3. **Incremental Processing**: Support for batch and streaming data processing
4. **Extensibility**: Easy addition of new entity types, extractors, and data sources

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
│  - Metadata preservation                 │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│      Local Storage (JSON)                │
└─────────────────────────────────────────┘
```
**Key Technologies:**
- `wikipedia-api`: Python wrapper for Wikipedia API
- JSON for intermediate storage
- SQLite for metadata and caching

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
│   GLiNER     │ │    spaCy     │ │   Custom     │
│  Zero-shot   │ │  Pre-trained │ │  Extractors  │
│     NER      │ │     NER      │ │   (Future)   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────┐
│         Entity Resolution                │
│  - Deduplication                         │
│  - Coreference resolution                ││  - Confidence scoring                    │
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

3. **Ensemble Strategy**:
   - Union of entities from both models
   - Confidence-weighted deduplication
   - Majority voting for conflicts

### 3. Graph Construction Layer

```
┌─────────────────────────────────────────┐
│         Entity Nodes                     │
│  - ID, Label, Value                      │
│  - Confidence, Source                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐│      Relationship Extraction             │
│  - Co-occurrence (same sentence)         │
│  - Dependency parsing                    │
│  - Pattern matching                      │
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
│  - JSON (debugging)                      │
└─────────────────────────────────────────┘
```

**Graph Schema:**

```python
# Node structure
node = {
    'id': 'uuid4',
    'label': 'PERSON|ORG|LOCATION|...',
    'value': 'Entity text',
    'confidence': 0.0-1.0,    'sources': ['article_id1', 'article_id2'],
    'contexts': ['surrounding text snippets']
}

# Edge structure
edge = {
    'source': 'node_id1',
    'target': 'node_id2',
    'type': 'RELATED_TO|MENTIONS|LOCATED_IN|...',
    'weight': 0.0-1.0,
    'confidence': 0.0-1.0,
    'contexts': ['relationship contexts']
}
```

### 4. Validation Layer

```
┌─────────────────────────────────────────┐
│         Streamlit Web UI                 │
│  ┌────────────────────────────────────┐ │
│  │     Graph Visualization (PyVis)     │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │      Entity Table (Pandas)          │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │     Validation Controls              │ │
│  │  - Approve/Reject                   │ │
│  │  - Merge duplicates                 │ │
│  │  - Edit properties                  │ ││  └────────────────────────────────────┘ │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│        Graph Update Engine               │
│  - Atomic operations                     │
│  - Audit logging                         │
│  - Version control                       │
└─────────────────────────────────────────┘
```

### 5. Query Layer (RAG)

```
┌─────────────────────────────────────────┐
│           User Query                     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       Query Understanding                │
│  - Entity extraction from query          │
│  - Intent classification                 │
└────────────┬────────────────────────────┘
             │
             ├──────────────┬──────────────┐
             ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Vector     │ │    Graph     │ │   Hybrid     ││   Search     │ │  Traversal   │ │   Search     │
│  (ChromaDB)  │ │ (NetworkX)   │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       └────────────────┴────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────┐
│         Context Assembly                 │
│  - Relevant entities                     │
│  - Relationship paths                    │
│  - Source documents                      │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│          LLM Generation                  │
│  - Prompt engineering                    │
│  - Context injection                     │
│  - Response generation                   │
│  - Citation extraction                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│         Response Formatting              │
│  - Answer text                           │
│  - Supporting entities                   │
│  - Confidence scores                     ││  - Visualization link                    │
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

### 4. Query Flow
```
User Query → Entity Recognition → Graph Retrieval → Context Building → LLM → Response
```

## Technology Stack Details

### Core Dependencies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.9+ | Core implementation |
| NER (Zero-shot) | GLiNER | Latest | Custom entity extraction |
| NER (Traditional) | spaCy | 3.7+ | Standard entity extraction |
| Graph Engine | NetworkX | 3.1+ | Graph manipulation || Visualization | PyVis | 0.3+ | Interactive graphs |
| Web UI | Streamlit | 1.28+ | Validation interface |
| Vector DB | ChromaDB | 0.4+ | Semantic search |
| LLM Runtime | Ollama | Latest | Local LLM hosting |
| Data Processing | Pandas | 2.0+ | Data manipulation |

### Model Specifications

#### NER Models
- **GLiNER**: `urchade/gliner_multi_pii-v1` (50MB)
- **spaCy**: `en_core_web_sm` (12MB)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (80MB)

#### LLM Models (via Ollama)
- **Primary**: Phi-3 Mini (2.3GB)
- **Alternative**: Mistral 7B (4.1GB)
- **Fallback**: Llama 2 7B (3.8GB)

## Performance Characteristics

### Processing Metrics

| Operation | Target Time | Actual (PoC) |
|-----------|------------|--------------|
| Article ingestion | 1-2 sec/article | TBD |
| Entity extraction | 5-10 sec/article | TBD |
| Graph construction | <1 sec/100 entities | TBD |
| Query response | <10 seconds | TBD |
| Visualization render | <2 seconds | TBD |
### Resource Requirements

- **Memory**: 4-8GB RAM (depending on graph size)
- **Storage**: 10GB (models + data)
- **CPU**: 4+ cores recommended
- **GPU**: Optional (speeds up embedding generation)

## Security Considerations

### Data Privacy
- All processing occurs locally
- No external API calls except Wikipedia (read-only)
- No telemetry or usage tracking
- User data never leaves the machine

### Input Validation
- Sanitize all user inputs
- Rate limiting on API calls
- Size limits on graph operations
- Timeout on long-running processes

## Scaling Considerations

### Current Limitations (PoC)
- Single-threaded processing
- In-memory graph storage
- Limited to 1000 nodes
- No distributed processing

### Production Path
1. **Phase 1**: Multi-threading for extraction
2. **Phase 2**: Graph database (Neo4j) integration
3. **Phase 3**: Distributed processing with Ray/Dask
4. **Phase 4**: API service with caching layer
## API Design (Future)

### RESTful Endpoints
```
POST   /api/ingest/wikipedia      # Ingest articles
GET    /api/graph/entities        # List entities
POST   /api/graph/validate        # Validate entities
DELETE /api/graph/entities/{id}   # Remove entity
POST   /api/query                 # Query the graph
GET    /api/visualization         # Get graph viz data
```

### WebSocket Events
```
graph:updated     # Graph modification
entity:extracted  # New entity found
query:processing  # Query in progress
```

## Error Handling Strategy

### Graceful Degradation
1. **NER Failure**: Fall back to single model
2. **LLM Unavailable**: Return graph-only results
3. **Memory Limit**: Implement graph pruning
4. **API Timeout**: Cache and retry

### Error Recovery
- Checkpoint during long operations
- Automatic retry with exponential backoff
- Persistent queue for failed operations
- Comprehensive error logging

## Monitoring & Observability
### Metrics to Track
- Entity extraction rate and accuracy
- Graph size and complexity metrics
- Query response times
- Memory and CPU usage
- Cache hit rates
- Model inference times

### Logging Strategy
```python
# Structured logging format
{
    "timestamp": "2024-01-01T12:00:00Z",
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
3. Download models
4. Run tests
5. Start Streamlit app

### Testing Strategy
- Unit tests for each module
- Integration tests for pipelines- End-to-end tests with sample data
- Performance benchmarks
- Model accuracy evaluation

### CI/CD Pipeline (Future)
```yaml
stages:
  - lint
  - test
  - build
  - benchmark
  - deploy
```

## Configuration Management

### Environment-Specific Configs
- `config.dev.yaml`: Development settings
- `config.test.yaml`: Test settings
- `config.prod.yaml`: Production settings

### Configuration Hierarchy
1. Default values in code
2. Configuration files
3. Environment variables
4. Command-line arguments

## Future Enhancements

### Short-term (3 months)
- [ ] Multi-language support
- [ ] Custom relationship extractors
- [ ] Advanced deduplication
- [ ] Batch processing optimization

### Medium-term (6 months)
- [ ] Real-time streaming pipeline
- [ ] Graph database integration- [ ] REST API implementation
- [ ] Docker containerization

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
- Ensemble: Best of both worlds

### Why Ollama?
- Truly local LLM execution
- Simple API
- Model management built-in
- Good model selection

### Why Streamlit?
- Rapid prototyping
- Built-in components for data apps
- No frontend development needed
- Good enough for PoC validation

---*Last Updated: December 2024*
*Version: 1.0 (PoC)*