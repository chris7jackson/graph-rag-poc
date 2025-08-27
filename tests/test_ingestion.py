"""
Tests for the ingestion module
"""

import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch

from src.ingestion import WikipediaIngester


class TestWikipediaIngester:
    """Test cases for WikipediaIngester."""
    
    def test_initialization(self):
        """Test ingester initialization."""
        config = {'language': 'en', 'cache_dir': './test_cache'}
        ingester = WikipediaIngester(config)
        
        assert ingester.language == 'en'
        assert ingester.cache_dir == Path('./test_cache')
    
    def test_default_initialization(self):
        """Test ingester with default config."""
        ingester = WikipediaIngester()
        
        assert ingester.language == 'en'
        assert ingester.cache_dir.exists()
    
    @patch('src.ingestion.wikipedia.wikipedia.page')    def test_fetch_article_success(self, mock_page):
        """Test successful article fetching."""
        # Mock Wikipedia page
        mock_page_obj = Mock()
        mock_page_obj.title = "Test Article"
        mock_page_obj.url = "http://test.url"
        mock_page_obj.content = "Test content"
        mock_page_obj.summary = "Test summary"
        mock_page_obj.categories = ["Category1", "Category2"]
        mock_page_obj.links = ["Link1", "Link2"]
        mock_page.return_value = mock_page_obj
        
        ingester = WikipediaIngester()
        article = ingester.fetch_article("Test Article")
        
        assert article is not None
        assert article['title'] == "Test Article"
        assert article['content'] == "Test content"
        assert 'fetch_timestamp' in article
    
    @patch('src.ingestion.wikipedia.wikipedia.page')
    def test_fetch_article_not_found(self, mock_page):
        """Test article not found error."""
        import wikipedia
        mock_page.side_effect = wikipedia.exceptions.PageError("Page not found")
        
        ingester = WikipediaIngester()
        article = ingester.fetch_article("NonExistent")        
        assert article is None
    
    def test_save_article(self, tmp_path):
        """Test article saving."""
        ingester = WikipediaIngester()
        ingester.output_dir = tmp_path
        
        article = {
            'title': 'Test Article',
            'content': 'Test content',
            'url': 'http://test.url'
        }
        
        filepath = ingester.save_article(article)
        
        assert Path(filepath).exists()
        
        # Load and verify saved content
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        
        assert loaded['title'] == article['title']
        assert loaded['content'] == article['content']


if __name__ == "__main__":
    pytest.main([__file__])