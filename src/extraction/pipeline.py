"""
Entity Extraction Pipeline

Combines GLiNER and spaCy for comprehensive entity extraction.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np

import spacy
from spacy.tokens import Doc
from tqdm import tqdm
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class EntityExtractor:
    """Base class for entity extraction."""
    
    def __init__(self, config: Dict = None):
        """Initialize the entity extractor."""
        self.config = config or {}
        self.confidence_threshold = self.config.get('confidence_threshold', 0.5)
        
    def extract(self, text: str) -> List[Dict]:
        """
        Extract entities from text.
        
        Args:            text: Input text
            
        Returns:
            List of entity dictionaries
        """
        raise NotImplementedError


class SpacyExtractor(EntityExtractor):
    """Entity extraction using spaCy."""
    
    def __init__(self, config: Dict = None):
        """Initialize spaCy extractor."""
        super().__init__(config)
        self.model_name = self.config.get('model_name', 'en_core_web_sm')
        
        try:
            self.nlp = spacy.load(self.model_name)
        except OSError:
            console.print(f"[yellow]Model {self.model_name} not found. Installing...[/yellow]")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", self.model_name])
            self.nlp = spacy.load(self.model_name)
        
        logger.info(f"Loaded spaCy model: {self.model_name}")
    
    def extract(self, text: str) -> List[Dict]:
        """Extract entities using spaCy."""
        doc = self.nlp(text)
        entities = []        
        for ent in doc.ents:
            entity = {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': 1.0,  # spaCy doesn't provide confidence scores
                'extractor': 'spacy'
            }
            entities.append(entity)
        
        return entities
    
    def extract_relationships(self, text: str) -> List[Tuple]:
        """Extract relationships using dependency parsing."""
        doc = self.nlp(text)
        relationships = []
        
        for token in doc:
            if token.dep_ in ("nsubj", "dobj", "pobj"):
                for child in token.children:
                    if child.dep_ in ("prep", "agent"):
                        relationships.append((
                            token.text,
                            child.text,
                            token.head.text
                        ))
        
        return relationships

class CombinedExtractor:
    """Combines multiple extractors for comprehensive entity extraction."""
    
    def __init__(self, config: Dict = None):
        """Initialize combined extractor."""
        self.config = config or {}
        self.spacy_extractor = SpacyExtractor(self.config.get('spacy', {}))
        # GLiNER would be initialized here when available
        self.output_dir = Path('./data/entities')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_from_text(self, text: str, doc_id: str = None) -> Dict:
        """
        Extract entities from text using all extractors.
        
        Args:
            text: Input text
            doc_id: Document identifier
            
        Returns:
            Dictionary containing entities and metadata
        """
        console.print("[blue]Extracting entities...[/blue]")
        
        # Extract with spaCy
        spacy_entities = self.spacy_extractor.extract(text)
        
        # Combine and deduplicate
        all_entities = self._deduplicate_entities(spacy_entities)        
        # Extract relationships
        relationships = self.spacy_extractor.extract_relationships(text)
        
        result = {
            'doc_id': doc_id,
            'entities': all_entities,
            'relationships': relationships,
            'stats': {
                'total_entities': len(all_entities),
                'unique_entities': len(set(e['text'] for e in all_entities)),
                'total_relationships': len(relationships)
            }
        }
        
        logger.info(f"Extracted {len(all_entities)} entities from document {doc_id}")
        return result
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Deduplicate entities based on text and position."""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity['text'].lower(), entity['label'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities    
    def process_articles(self, articles_dir: str) -> List[Dict]:
        """
        Process all articles in a directory.
        
        Args:
            articles_dir: Directory containing article JSON files
            
        Returns:
            List of extraction results
        """
        articles_path = Path(articles_dir)
        article_files = list(articles_path.glob('*.json'))
        
        if not article_files:
            console.print(f"[red]No articles found in {articles_dir}[/red]")
            return []
        
        results = []
        
        for article_file in tqdm(article_files, desc="Processing articles"):
            with open(article_file, 'r', encoding='utf-8') as f:
                article = json.load(f)
            
            # Extract entities
            extraction_result = self.extract_from_text(
                article['content'], 
                doc_id=article['title']
            )
            
            results.append(extraction_result)            
            # Save extraction result
            self.save_extraction(extraction_result)
        
        console.print(f"[green]Processed {len(results)} articles[/green]")
        return results
    
    def save_extraction(self, result: Dict):
        """Save extraction results to JSON."""
        safe_id = "".join(c for c in result['doc_id'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_id = safe_id.replace(' ', '_')[:100]
        
        filename = f"{safe_id}_entities.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved extraction results to {filepath}")


def main():
    """Main function for testing extraction pipeline."""
    extractor = CombinedExtractor()
    
    # Process articles
    results = extractor.process_articles('./data/articles')
    
    # Print statistics
    total_entities = sum(r['stats']['total_entities'] for r in results)
    total_relationships = sum(r['stats']['total_relationships'] for r in results)
    
    console.print("\n[bold]Extraction Statistics:[/bold]")
    console.print(f"Total entities extracted: {total_entities}")
    console.print(f"Total relationships extracted: {total_relationships}")
    console.print(f"Average entities per article: {total_entities / len(results):.1f}")


if __name__ == "__main__":
    main()