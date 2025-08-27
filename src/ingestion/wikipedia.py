"""
Wikipedia Article Ingestion Module

This module handles fetching and preprocessing Wikipedia articles.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
import time

import wikipedia
from tqdm import tqdm
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


class WikipediaIngester:
    """Handles Wikipedia article ingestion and preprocessing."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Wikipedia ingester.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.language = self.config.get('language', 'en')
        self.user_agent = self.config.get('user_agent', 'GraphRAGPoC/1.0')        self.cache_dir = Path(self.config.get('cache_dir', './data/cache'))
        self.output_dir = Path('./data/articles')
        
        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set Wikipedia language
        wikipedia.set_lang(self.language)
        
    def fetch_article(self, title: str) -> Optional[Dict]:
        """
        Fetch a single Wikipedia article.
        
        Args:
            title: Article title to fetch
            
        Returns:
            Dictionary containing article data or None if failed
        """
        try:
            console.print(f"[blue]Fetching article: {title}[/blue]")
            page = wikipedia.page(title)
            
            article_data = {
                'title': page.title,
                'url': page.url,
                'content': page.content,
                'summary': page.summary,
                'categories': page.categories[:10],  # Limit categories                'links': page.links[:50],  # Limit links
                'fetch_timestamp': time.time()
            }
            
            logger.info(f"Successfully fetched article: {title}")
            return article_data
            
        except wikipedia.exceptions.DisambiguationError as e:
            console.print(f"[yellow]Disambiguation for {title}. Options: {e.options[:5]}[/yellow]")
            # Try first option
            if e.options:
                return self.fetch_article(e.options[0])
            return None
            
        except wikipedia.exceptions.PageError:
            console.print(f"[red]Page not found: {title}[/red]")
            logger.error(f"Page not found: {title}")
            return None
            
        except Exception as e:
            console.print(f"[red]Error fetching {title}: {str(e)}[/red]")
            logger.error(f"Error fetching {title}: {str(e)}")
            return None
    
    def fetch_articles(self, topics: List[str], max_articles: int = 10) -> List[Dict]:
        """
        Fetch multiple Wikipedia articles.
        
        Args:            topics: List of topics to search for
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        with console.status("[bold green]Fetching Wikipedia articles...") as status:
            for topic in tqdm(topics[:max_articles], desc="Fetching articles"):
                article = self.fetch_article(topic)
                if article:
                    articles.append(article)
                    self.save_article(article)
                
                # Rate limiting
                time.sleep(0.5)
        
        console.print(f"[green]Successfully fetched {len(articles)} articles[/green]")
        return articles
    
    def save_article(self, article: Dict) -> str:
        """
        Save article to JSON file.
        
        Args:
            article: Article dictionary
            
        Returns:            Path to saved file
        """
        # Create safe filename
        safe_title = "".join(c for c in article['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:100]
        
        filename = f"{safe_title}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved article to {filepath}")
        return str(filepath)
    
    def search_articles(self, query: str, results: int = 5) -> List[str]:
        """
        Search for Wikipedia articles.
        
        Args:
            query: Search query
            results: Number of results to return
            
        Returns:
            List of article titles
        """
        try:
            search_results = wikipedia.search(query, results=results)
            console.print(f"[blue]Found {len(search_results)} articles for '{query}'[/blue]")
            return search_results        except Exception as e:
            logger.error(f"Search failed for '{query}': {str(e)}")
            return []


def main():
    """Main function for testing the ingestion module."""
    # Example usage
    ingester = WikipediaIngester()
    
    # Test topics
    test_topics = [
        "Artificial Intelligence",
        "Machine Learning",
        "Natural Language Processing",
        "Computer Vision",
        "Deep Learning"
    ]
    
    # Fetch articles
    articles = ingester.fetch_articles(test_topics, max_articles=5)
    
    console.print(f"\n[bold green]Ingestion complete![/bold green]")
    console.print(f"Fetched {len(articles)} articles")
    console.print(f"Articles saved to: {ingester.output_dir}")


if __name__ == "__main__":
    main()