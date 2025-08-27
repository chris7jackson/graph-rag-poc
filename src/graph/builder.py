"""
Graph Builder Module

Constructs NetworkX graphs from extracted entities and relationships.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

import networkx as nx
from pyvis.network import Network
from tqdm import tqdm
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class GraphBuilder:
    """Builds and manages knowledge graphs."""
    
    def __init__(self, config: Dict = None):
        """Initialize graph builder."""
        self.config = config or {}
        self.graph = nx.DiGraph()
        self.output_dir = Path('./data/graphs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.min_confidence = self.config.get('min_confidence', 0.3)
        self.max_nodes = self.config.get('max_nodes', 1000)
        self.merge_threshold = self.config.get('merge_threshold', 0.85)
        
    def add_entity(self, entity: Dict, doc_id: str = None):
        """
        Add an entity as a node to the graph.
        
        Args:
            entity: Entity dictionary
            doc_id: Document identifier
        """
        node_id = f"{entity['text']}_{entity['label']}"
        
        if node_id not in self.graph:
            self.graph.add_node(
                node_id,
                text=entity['text'],
                label=entity['label'],
                confidence=entity.get('confidence', 1.0),
                sources=[doc_id] if doc_id else [],
                count=1
            )
        else:
            # Update existing node
            node_data = self.graph.nodes[node_id]
            node_data['count'] += 1
            if doc_id and doc_id not in node_data['sources']:
                node_data['sources'].append(doc_id)
            # Update confidence (average)
            old_conf = node_data['confidence']
            new_conf = entity.get('confidence', 1.0)
            node_data['confidence'] = (old_conf * (node_data['count'] - 1) + new_conf) / node_data['count']
    
    def add_relationship(self, source: str, target: str, rel_type: str = "RELATED_TO", weight: float = 1.0):
        """
        Add a relationship as an edge to the graph.
        
        Args:
            source: Source entity
            target: Target entity
            rel_type: Relationship type
            weight: Edge weight
        """
        # Create node IDs (simple approach - in production, would need better entity resolution)
        source_nodes = [n for n in self.graph.nodes if self.graph.nodes[n]['text'] == source]
        target_nodes = [n for n in self.graph.nodes if self.graph.nodes[n]['text'] == target]
        
        if source_nodes and target_nodes:
            source_id = source_nodes[0]
            target_id = target_nodes[0]
            
            if self.graph.has_edge(source_id, target_id):
                # Update existing edge
                self.graph[source_id][target_id]['weight'] += weight
                self.graph[source_id][target_id]['count'] += 1
            else:
                # Add new edge
                self.graph.add_edge(
                    source_id,
                    target_id,
                    type=rel_type,
                    weight=weight,
                    count=1
                )
    
    def build_from_extractions(self, extraction_files: List[Path]) -> nx.DiGraph:
        """
        Build graph from extraction JSON files.
        
        Args:
            extraction_files: List of extraction result files
            
        Returns:
            NetworkX graph
        """
        console.print("[blue]Building graph from extractions...[/blue]")
        
        for file_path in tqdm(extraction_files, desc="Processing extractions"):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add entities
            for entity in data['entities']:
                if entity.get('confidence', 1.0) >= self.min_confidence:
                    self.add_entity(entity, data['doc_id'])
            
            # Add relationships from co-occurrence
            self._add_cooccurrence_edges(data['entities'], data['doc_id'])
        
        # Prune graph if needed
        if len(self.graph.nodes) > self.max_nodes:
            self._prune_graph()
        
        console.print(f"[green]Graph built with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges[/green]")
        return self.graph
    
    def _add_cooccurrence_edges(self, entities: List[Dict], doc_id: str):
        """Add edges based on entity co-occurrence."""
        # Simple approach: connect entities that appear in the same document
        entity_texts = [e['text'] for e in entities if e.get('confidence', 1.0) >= self.min_confidence]
        
        for i, source in enumerate(entity_texts):
            for target in entity_texts[i+1:i+5]:  # Connect to next 4 entities (windowed approach)
                if source != target:
                    self.add_relationship(source, target, "CO_OCCURS", weight=0.5)
    
    def _prune_graph(self):
        """Prune graph to maximum size."""
        # Keep nodes with highest degree centrality
        centrality = nx.degree_centrality(self.graph)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        nodes_to_keep = [node for node, _ in sorted_nodes[:self.max_nodes]]        
        # Create subgraph with top nodes
        self.graph = self.graph.subgraph(nodes_to_keep).copy()
        logger.info(f"Pruned graph to {len(self.graph.nodes)} nodes")
    
    def save_graph(self, filename: str = "knowledge_graph"):
        """
        Save graph in multiple formats.
        
        Args:
            filename: Base filename for saved graph
        """
        # Save as pickle
        pickle_path = self.output_dir / f"{filename}.pickle"
        with open(pickle_path, 'wb') as f:
            pickle.dump(self.graph, f)
        console.print(f"[green]Saved graph to {pickle_path}[/green]")
        
        # Save as GraphML (with cleaned data)
        graphml_path = self.output_dir / f"{filename}.graphml"
        cleaned_graph = self._prepare_graph_for_graphml()
        nx.write_graphml(cleaned_graph, graphml_path)
        console.print(f"[green]Saved graph to {graphml_path}[/green]")
        
        # Save statistics
        self._save_statistics(filename)
    
    def _prepare_graph_for_graphml(self) -> nx.DiGraph:
        """Prepare graph for GraphML export by converting unsupported data types."""
        cleaned_graph = nx.DiGraph()
        
        # Copy nodes with cleaned attributes
        for node, data in self.graph.nodes(data=True):
            cleaned_data = {}
            for key, value in data.items():
                if isinstance(value, list):
                    cleaned_data[key] = str(value)  # Convert lists to strings
                elif isinstance(value, (int, float, str, bool)):
                    cleaned_data[key] = value
                else:
                    cleaned_data[key] = str(value)  # Convert other types to strings
            cleaned_graph.add_node(node, **cleaned_data)
        
        # Copy edges with cleaned attributes
        for source, target, data in self.graph.edges(data=True):
            cleaned_data = {}
            for key, value in data.items():
                if isinstance(value, list):
                    cleaned_data[key] = str(value)  # Convert lists to strings
                elif isinstance(value, (int, float, str, bool)):
                    cleaned_data[key] = value
                else:
                    cleaned_data[key] = str(value)  # Convert other types to strings
            cleaned_graph.add_edge(source, target, **cleaned_data)
        
        return cleaned_graph
    
    def _save_statistics(self, filename: str):
        """Save graph statistics."""
        stats = {
            'nodes': len(self.graph.nodes),
            'edges': len(self.graph.edges),
            'density': nx.density(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes) if self.graph.nodes else 0,
            'connected_components': nx.number_weakly_connected_components(self.graph),
            'entity_types': self._count_entity_types(),
            'top_entities': self._get_top_entities(10)
        }
        
        stats_path = self.output_dir / f"{filename}_stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        console.print(f"[green]Saved statistics to {stats_path}[/green]")
    
    def _count_entity_types(self) -> Dict[str, int]:
        """Count entities by type."""
        type_counts = defaultdict(int)
        for node, data in self.graph.nodes(data=True):
            type_counts[data.get('label', 'UNKNOWN')] += 1
        return dict(type_counts)
    
    def _get_top_entities(self, n: int = 10) -> List[Tuple[str, float]]:
        """Get top n entities by degree centrality."""
        centrality = nx.degree_centrality(self.graph)
        sorted_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return [(self.graph.nodes[node]['text'], score) for node, score in sorted_entities[:n]]
    def visualize(self, output_file: str = "graph.html", max_nodes: int = 100):
        """
        Create interactive visualization of the graph.
        
        Args:
            output_file: Output HTML file
            max_nodes: Maximum nodes to visualize
        """
        # Select top nodes if graph is too large
        if len(self.graph.nodes) > max_nodes:
            centrality = nx.degree_centrality(self.graph)
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            subgraph = self.graph.subgraph([node for node, _ in top_nodes])
        else:
            subgraph = self.graph
        
        # Create PyVis network
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        net.from_nx(subgraph)
        
        # Customize visualization
        net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250, spring_strength=0.001, damping=0.09)
        
        # Save visualization
        output_path = self.output_dir / output_file
        net.save_graph(str(output_path))
        console.print(f"[green]Saved visualization to {output_path}[/green]")

def main():
    """Main function for testing graph builder."""
    builder = GraphBuilder()
    
    # Load extraction results
    extraction_dir = Path('./data/entities')
    extraction_files = list(extraction_dir.glob('*_entities.json'))
    
    if not extraction_files:
        console.print("[red]No extraction files found. Run extraction pipeline first.[/red]")
        return
    
    # Build graph
    graph = builder.build_from_extractions(extraction_files)
    
    # Save graph
    builder.save_graph()
    
    # Create visualization
    builder.visualize()
    
    # Print summary
    console.print("\n[bold]Graph Summary:[/bold]")
    console.print(f"Nodes: {len(graph.nodes)}")
    console.print(f"Edges: {len(graph.edges)}")
    console.print(f"Density: {nx.density(graph):.4f}")


if __name__ == "__main__":
    main()