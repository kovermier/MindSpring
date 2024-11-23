import json
from memlog.conversation_vector_store import ConversationVectorStore

# Initialize vector store
vector_store = ConversationVectorStore()

# Load test conversation
with open('test_conversation.json', 'r') as f:
    test_conv = json.load(f)

# Process the conversation
print("Loading test conversation...")
vector_store.process_conversations([test_conv])

# Test search
print("\nTesting search...")
results = vector_store.search("capital of France", limit=1)
print("Search results:", results)

# Get stats
stats = vector_store.get_collection_stats()
print("\nCollection stats:", stats)
