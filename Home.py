import streamlit as st
st.set_page_config(
    page_title="MindSpring",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

import html
from datetime import datetime
from memlog.shared_vector_store import get_shared_vector_store

def format_timestamp(ts):
    """Convert ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return ts

def format_message_content(text):
    """Format message content for safe HTML display"""
    if not text:
        return ""
    text = html.escape(text)
    text = text.replace('\n', '<br>')
    return text

def display_conversation_list(conversations, search_term="", page_size=10, page_number=1):
    """Display a list of conversations with filtering, search, and pagination"""
    st.markdown("### 📝 Search Results")
    
    # Pagination
    total_conversations = len(conversations)
    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, total_conversations)
    paginated_conversations = conversations[start_index:end_index]
    
    # Display conversation count and pagination controls
    st.info(f"Found {total_conversations} conversations. Showing {len(paginated_conversations)} on page {page_number}")
    
    if total_conversations > page_size:
        cols = st.columns([1, 1, 4])
        with cols[0]:
            if page_number > 1:
                if st.button("← Previous"):
                    st.session_state.page_number -= 1
                    st.rerun()
        with cols[1]:
            if page_number * page_size < total_conversations:
                if st.button("Next →"):
                    st.session_state.page_number += 1
                    st.rerun()
    
    # Create a scrollable container for conversations
    for conv in paginated_conversations:
        with st.expander(f"🗣️ {conv['title']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Created:** {format_timestamp(conv['create_time'])}")
                st.markdown(f"**Preview:** {conv['text'][:200]}...")
                if 'score' in conv:
                    st.markdown(f"**Relevance Score:** {conv['score']:.2f}")
            
            with col2:
                if st.button("View Details", key=f"view_{conv['id']}"):
                    st.session_state.selected_conversation = conv
                    st.session_state.view_mode = "detail"

def display_conversation_detail(conversation):
    """Display detailed view of a single conversation"""
    # Add back button
    if st.button("← Back to Search"):
        st.session_state.view_mode = "list"
        st.session_state.selected_conversation = None
        st.rerun()
    
    st.markdown(f"## 🗣️ {conversation['title']}")
    
    # Create tabs for different aspects of the conversation
    tab1, tab2 = st.tabs(["💬 Content", "ℹ️ Details"])
    
    with tab1:
        st.markdown(f"""
        <div class="conversation-content">
            {format_message_content(conversation['text'])}
        </div>
        """, unsafe_allow_html=True)
            
    with tab2:
        st.markdown("### Conversation Details")
        st.markdown(f"**Created:** {format_timestamp(conversation['create_time'])}")
        if 'id' in conversation:
            st.code(f"ID: {conversation['id']}")
        
        # Show similar conversations
        st.markdown("### Similar Conversations")
        vector_store = get_shared_vector_store()
        if vector_store:
            similar = vector_store.search(
                conversation['text'],
                limit=3,
                score_threshold=0.3
            )
            for r in similar:
                if str(r['id']) != str(conversation['id']):
                    st.markdown(
                        f"""<div class="similar-conversation">
                            <h4>{r['title']}</h4>
                            <p>Similarity Score: {r['score']:.2f}</p>
                            <p>{r['text'][:200]}...</p>
                        </div>""",
                        unsafe_allow_html=True
                    )

# Add custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    .conversation-content {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        border: 1px solid #3d3d3d;
        white-space: pre-wrap;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    .search-container {
        background-color: #2d2d2d;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin-bottom: 25px;
        border: 1px solid #3d3d3d;
    }
    .similar-conversation {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #3d3d3d;
    }
    .empty-state {
        text-align: center;
        padding: 40px;
        background: #2d2d2d;
        border-radius: 8px;
        margin: 20px 0;
    }
    .loading-progress {
        margin-top: 20px;
        padding: 15px;
        background: #2d2d2d;
        border-radius: 8px;
        border: 1px solid #3d3d3d;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "list"
if 'selected_conversation' not in st.session_state:
    st.session_state.selected_conversation = None
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

# Main app
st.title('🧠 MindSpring')
st.markdown("""
Welcome to MindSpring - your intelligent conversation explorer. Search through your chat history,
discover patterns, and explore topic relationships.

Use the sidebar to switch between different views:
- 💬 **Search** (current page): Search and browse through your chat history
- 🕸️ **Topic Map**: Explore conversation relationships and topic clusters
""")

# Initialize vector store
vector_store = get_shared_vector_store()

# Sidebar controls
st.sidebar.title("Search Controls")

# Add Load Data button to sidebar
if st.sidebar.button("🔄 Load All Conversations", use_container_width=True):
    if vector_store is None:
        st.error("❌ Vector store initialization failed. Please check if Ollama is running.")
    else:
        with st.spinner("Loading conversations..."):
            try:
                # Get stats to check if we have conversations
                stats = vector_store.get_collection_stats()
                if stats.get('points_count', 0) > 0:
                    st.success(f"✅ Found {stats['points_count']:,} conversations!")
                    # Load first batch of conversations
                    results = vector_store.search("", limit=100, score_threshold=0.0)
                    st.session_state.conversations = [
                        {
                            'id': r['id'],
                            'title': r['title'],
                            'text': r['text'],
                            'create_time': r['create_time']
                        }
                        for r in results
                    ]
                    st.rerun()
                else:
                    st.warning("No conversations found in the vector store.")
            except Exception as e:
                st.error(f"❌ Error loading conversations: {str(e)}")

# Search interface
st.markdown("### 🔍 Semantic Search")
with st.container():
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input(
            "Search conversations",
            placeholder="Enter keywords or phrases to search...",
            help="Uses semantic search to find relevant conversations"
        )
    with search_col2:
        threshold = st.select_slider(
            "Relevance",
            options=["Low", "Medium", "High"],
            value="Medium",
            help="Adjust how closely results must match your search"
        )
        
        # Map text values to numbers
        score_threshold = {
            "Low": 0.2,
            "Medium": 0.3,
            "High": 0.4
        }[threshold]

if search_term and vector_store:
    try:
        results = vector_store.search(
            search_term,
            limit=100,
            score_threshold=score_threshold
        )
        st.session_state.conversations = [
            {
                'id': r['id'],
                'title': r['title'],
                'text': r['text'],
                'create_time': r['create_time'],
                'score': r['score']
            }
            for r in results
        ]
    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")

# Display conversations based on view mode
if st.session_state.view_mode == "list":
    display_conversation_list(
        st.session_state.conversations,
        search_term,
        page_number=st.session_state.page_number
    )
else:
    display_conversation_detail(st.session_state.selected_conversation)
