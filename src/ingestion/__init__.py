"""
Ingestion module for the Graph RAG pipeline.

Handles data ingestion from various sources, primarily Wikipedia.
"""

from .wikipedia import WikipediaIngester

__all__ = ['WikipediaIngester']