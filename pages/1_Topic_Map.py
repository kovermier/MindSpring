import streamlit as st
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config
from memlog.shared_vector_store import get_shared_vector_store

# Page configuration
st.set_page_config(
    page_title="MindSpring - Topic Map",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main > div { padding-top: 0; }
    .graph-container {
        margin: 1rem;
        padding: 1rem;
        background: #1E1E1E;
        border-radius: 10px;
        height: 800px;
    }
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    .conversation-card {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #3d3d3d;
    }
    .message-content {
        background: #1f1f1f;
        padding: 10px;
        border-radius: 4px;
        margin: 5px 0;
        border-left: 3px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

def create_knowledge_graph(conversations, min_similarity=0.3, vector_store=None):
    """Create knowledge graph from conversations using vector similarity."""
    nodes = []
    edges = []
    
    # Create nodes
    with st.spinner("Processing conversations..."):
        for conv in conversations:
            conv_id = str(conv['id'])
            conv_title = conv.get('title', f'Conversation {conv_id}')
            
            # Create node
            nodes.append(Node(
                id=conv_id,
                label=conv_title[:30] + "..." if len(conv_title) > 30 else conv_title,
                title=conv_title,
                size=40,
                color="#4CAF50"
            ))
    
    # Create edges using vector similarity
    if len(nodes) >= 2 and vector_store:
        with st.spinner("Generating conversation connections..."):
            processed_pairs = set()
            
            for node1 in nodes:
                # Get similar conversations for the current node
                results = vector_store.search(
                    node1.title,
                    limit=5,
                    score_threshold=min_similarity
                )
                
                for result in results:
                    # Skip self-connections
                    if str(result['id']) == node1.id:
                        continue
                        
                    pair_key = f"{min(node1.id, str(result['id']))}-{max(node1.id, str(result['id']))}"
                    if pair_key not in processed_pairs:
                        edges.append(Edge(
                            source=node1.id,
                            target=str(result['id']),
                            label=f"{result['score']:.2f}",
                            color="#757575"
                        ))
                        processed_pairs.add(pair_key)
    
    return nodes, edges

# Main app
st.title('🕸️ Topic Map')
st.markdown("""
Explore relationships between your conversations through an interactive knowledge graph.
The connections between conversations are determined by semantic similarity.
""")

# Initialize vector store
vector_store = get_shared_vector_store()

# Sidebar controls
with st.sidebar:
    st.markdown("### Graph Settings")
    
    # Number of conversations to display
    items_per_page = st.selectbox(
        "Conversations to show",
        [10, 20, 50, 100],
        index=1,
        help="Number of conversations to include in the graph"
    )
    
    # Similarity threshold control
    similarity = st.select_slider(
        "Connection Strength",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="Controls how closely related conversations need to be to show connections"
    )
    
    # Map text values to numbers
    similarity_threshold = {
        "Low": 0.2,
        "Medium": 0.3,
        "High": 0.4
    }[similarity]
    
    # Topic filter
    topic_filter = st.text_input(
        "Filter by Topic",
        "",
        help="Enter keywords to focus on specific topics"
    )

# Load and process data
try:
    if vector_store is None:
        st.error("❌ Vector store initialization failed. Please check if Ollama is running.")
    else:
        with st.spinner("Loading conversations..."):
            # Get conversations from vector store
            if topic_filter:
                results = vector_store.search(topic_filter, limit=items_per_page)
            else:
                results = vector_store.search("", limit=items_per_page, score_threshold=0.0)
            
            conversations = [
                {
                    'id': r['id'],
                    'title': r['title'],
                    'text': r['text'],
                    'create_time': r['create_time']
                }
                for r in results
            ]
        
        if conversations:
            nodes, edges = create_knowledge_graph(conversations, similarity_threshold, vector_store)
            
            if nodes and edges:
                # Graph configuration
                config = Config(
                    width=800,
                    height=600,
                    directed=False,
                    nodes={
                        'font': {'size': 16, 'color': '#ffffff'},
                        'borderWidth': 2,
                        'scaling': {'min': 30, 'max': 45}
                    },
                    edges={
                        'font': {'size': 12, 'color': '#ffffff'},
                        'smooth': {'enabled': True, 'type': 'continuous'}
                    },
                    physics={
                        'enabled': True,
                        'barnesHut': {
                            'gravitationalConstant': -2000,
                            'centralGravity': 0.3,
                            'springLength': 200,
                            'springConstant': 0.04,
                            'damping': 0.09,
                            'avoidOverlap': 0.1
                        }
                    },
                    interaction={
                        'hover': True,
                        'dragNodes': True,
                        'dragView': True,
                        'zoomView': True
                    }
                )
                
                # Display graph
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                selected_node = agraph(nodes=nodes, edges=edges, config=config)
                st.markdown('</div>', unsafe_allow_html=True)

                # Show selected conversation
                if selected_node:
                    st.sidebar.markdown("### Selected Conversation")
                    # Find selected conversation
                    selected_conv = next(
                        (c for c in conversations if str(c['id']) == selected_node),
                        None
                    )
                    if selected_conv:
                        st.sidebar.markdown(
                            f"""<div class="conversation-card">
                                <h3>{selected_conv['title']}</h3>
                                <p>Created: {selected_conv['create_time']}</p>
                                <div class="message-content">{selected_conv['text'][:500]}...</div>
                            </div>""",
                            unsafe_allow_html=True
                        )
                        
                        # Show similar conversations
                        st.sidebar.markdown("### Related Conversations")
                        similar = vector_store.search(
                            selected_conv['text'],
                            limit=3,
                            score_threshold=similarity_threshold
                        )
                        for r in similar:
                            if str(r['id']) != selected_node:
                                st.sidebar.markdown(
                                    f"""<div class="conversation-card">
                                        <h4>{r['title']}</h4>
                                        <p>Similarity: {r['score']:.2f}</p>
                                    </div>""",
                                    unsafe_allow_html=True
                                )

            else:
                st.warning(
                    "No connections found between conversations. "
                    "Try adjusting the connection strength to 'Low' or "
                    "increasing the number of conversations to show."
                )
        else:
            st.info("No conversations found. Try adjusting your topic filter or load some conversations first.")

except Exception as e:
    st.error(f"Error processing conversations: {str(e)}")
    st.write("Please check your vector store connection and try again.")
