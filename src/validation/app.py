"""
Streamlit Validation Interface for Graph RAG Pipeline

Interactive web interface for validating and editing the knowledge graph.
"""

import streamlit as st
import pickle
import json
from pathlib import Path
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="Graph RAG Validation",
    page_icon="🔍",
    layout="wide"
)

# Title and description
st.title("🔍 Graph RAG Validation Interface")
st.markdown("Interactive tool for validating and editing the knowledge graph")

# Define graph directory
graph_dir = Path('./data/graphs')

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    
    # Load graph
    if graph_dir.exists():
        graph_files = list(graph_dir.glob('*.pickle'))
        if graph_files:
            selected_graph = st.selectbox(
                "Select Graph",
                graph_files,
                format_func=lambda x: x.stem
            )
        else:
            st.warning("No graph files found")
            selected_graph = None
    else:
        st.warning("Graph directory not found")
        selected_graph = None
    
    if selected_graph:
        # Load graph
        with open(selected_graph, 'rb') as f:
            graph = pickle.load(f)
        st.success(f"Loaded graph with {len(graph.nodes)} nodes")
    else:
        graph = None

# Main interface tabs
if graph:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Entities", "🔗 Relationships", "📈 Visualization"])
    
    with tab1:
        st.header("Graph Overview")
                
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Nodes", len(graph.nodes))
        with col2:
            st.metric("Total Edges", len(graph.edges))
        with col3:
            st.metric("Graph Density", f"{nx.density(graph):.4f}")
        with col4:
            avg_degree = sum(dict(graph.degree()).values()) / len(graph.nodes) if graph.nodes else 0
            st.metric("Avg Degree", f"{avg_degree:.2f}")
        
        # Entity type distribution
        st.subheader("Entity Type Distribution")
        entity_types = {}
        for node, data in graph.nodes(data=True):
            label = data.get('label', 'UNKNOWN')
            entity_types[label] = entity_types.get(label, 0) + 1
        
        df_types = pd.DataFrame(
            list(entity_types.items()),
            columns=['Type', 'Count']
        ).sort_values('Count', ascending=False)
        
        st.bar_chart(df_types.set_index('Type'))
        
        # Top entities by degree centrality
        st.subheader("Top Entities by Connections")
        centrality = nx.degree_centrality(graph)
        top_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        df_top = pd.DataFrame([
            {
                'Entity': graph.nodes[node].get('text', node),
                'Type': graph.nodes[node].get('label', 'UNKNOWN'),
                'Connections': graph.degree(node),
                'Centrality': score
            }
            for node, score in top_entities
        ])
        
        st.dataframe(df_top, use_container_width=True)
    
    with tab2:
        st.header("Entity Management")
        
        # Entity search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Search entities", "")
        with col2:
            entity_type_filter = st.selectbox(
                "Filter by type",
                ['All'] + sorted(set(data.get('label', 'UNKNOWN') for _, data in graph.nodes(data=True)))
            )
                
        # Filter entities
        entities_data = []
        for node, data in graph.nodes(data=True):
            if entity_type_filter != 'All' and data.get('label') != entity_type_filter:
                continue
            if search_term and search_term.lower() not in data.get('text', '').lower():
                continue
            
            entities_data.append({
                'ID': node,
                'Text': data.get('text', ''),
                'Type': data.get('label', 'UNKNOWN'),
                'Confidence': data.get('confidence', 0),
                'Count': data.get('count', 0),
                'Sources': len(data.get('sources', []))
            })
        
        df_entities = pd.DataFrame(entities_data)
        
        if not df_entities.empty:
            # Display entities with selection
            selected_entities = st.data_editor(
                df_entities,
                use_container_width=True,
                num_rows="dynamic",
                disabled=['ID'],
                hide_index=True
            )            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Delete Selected", type="secondary"):
                    st.warning("Delete functionality would be implemented here")
            with col2:
                if st.button("Merge Duplicates"):
                    st.info("Merge functionality would be implemented here")
            with col3:
                if st.button("Export Entities"):
                    csv = df_entities.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="entities.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No entities match the current filters")
    
    with tab3:
        st.header("Relationship Management")
        
        # Get all edges with details
        edges_data = []
        for source, target, data in graph.edges(data=True):
            edges_data.append({
                'Source': graph.nodes[source].get('text', source),                'Target': graph.nodes[target].get('text', target),
                'Type': data.get('type', 'RELATED_TO'),
                'Weight': data.get('weight', 1.0),
                'Count': data.get('count', 1)
            })
        
        df_edges = pd.DataFrame(edges_data).sort_values('Weight', ascending=False)
        
        # Display top relationships
        st.subheader("Top Relationships")
        st.dataframe(df_edges.head(50), use_container_width=True)
        
        # Relationship statistics
        st.subheader("Relationship Statistics")
        rel_types = df_edges['Type'].value_counts()
        st.bar_chart(rel_types)
    
    with tab4:
        st.header("Graph Visualization")
        
        # Visualization options
        col1, col2, col3 = st.columns(3)
        with col1:
            max_nodes = st.slider("Max nodes to display", 10, 200, 50)
        with col2:
            layout = st.selectbox("Layout", ["force", "circular", "hierarchical"])
        with col3:
            show_labels = st.checkbox("Show labels", value=True)
                
        if st.button("Generate Visualization"):
            with st.spinner("Generating visualization..."):
                # Select top nodes by centrality
                centrality = nx.degree_centrality(graph)
                top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
                subgraph = graph.subgraph([node for node, _ in top_nodes])
                
                # Create PyVis network
                net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
                
                # Add nodes with colors based on type
                color_map = {
                    'PERSON': '#FF6B6B',
                    'ORGANIZATION': '#4ECDC4',
                    'LOCATION': '#45B7D1',
                    'DATE': '#96CEB4',
                    'EVENT': '#FECA57',
                    'TECHNOLOGY': '#9B59B6',
                    'CONCEPT': '#FD79A8'
                }
                
                for node, data in subgraph.nodes(data=True):
                    label = data.get('text', '') if show_labels else ""
                    color = color_map.get(data.get('label', 'UNKNOWN'), '#95A5A6')
                    size = 10 + (centrality.get(node, 0) * 50)
                    net.add_node(                        node,
                        label=label,
                        color=color,
                        size=size,
                        title=f"{data.get('text', '')}\nType: {data.get('label', 'UNKNOWN')}\nConfidence: {data.get('confidence', 0):.2f}"
                    )
                
                # Add edges
                for source, target, edge_data in subgraph.edges(data=True):
                    net.add_edge(source, target, weight=edge_data.get('weight', 1))
                
                # Set layout
                if layout == "force":
                    net.barnes_hut(gravity=-80000, central_gravity=0.3)
                elif layout == "hierarchical":
                    net.set_options("""
                    var options = {
                        "layout": {
                            "hierarchical": {
                                "enabled": true,
                                "direction": "UD"
                            }
                        }
                    }
                    """)
                
                # Save and display
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
                    net.save_graph(tmp.name)
                    with open(tmp.name, 'r') as f:
                        html_content = f.read()
                    
                    components.html(html_content, height=600, scrolling=True)
                
                st.success(f"Visualization generated with {len(subgraph.nodes)} nodes and {len(subgraph.edges)} edges")

else:
    st.warning("No graph loaded. Please run the pipeline first to generate a graph.")
    st.markdown("""
    ### Getting Started
    1. Run `python -m src.cli ingest` to fetch Wikipedia articles
    2. Run `python -m src.cli extract` to extract entities
    3. Run `python -m src.cli build` to build the graph
    4. Refresh this page to load the graph
    """)

# Footer
st.markdown("---")
st.markdown("Graph RAG Pipeline v0.1.0 - Proof of Concept")