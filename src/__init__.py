"""
Graph RAG Pipeline - Proof of Concept

A locally-executable pipeline for constructing knowledge graphs from Wikipedia articles
and enabling LLM-powered querying.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easier access
from . import ingestion
from . import extraction
from . import graph
from . import validation
from . import query

__all__ = [
    "ingestion",
    "extraction",
    "graph",
    "validation",
    "query",
]