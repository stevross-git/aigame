import ollama
import chromadb
import json
import os
from chromadb.utils import embedding_functions

# ==============================
# CONFIGURATION
# ==============================
MODEL_NAME = "sims-npc"  # The Ollama model you created
DATASET_FILE = "sims_npc_dataset.jsonl"  # Path to your dataset
DB_DIR = "./sims_npc_memory"  # Persistent ChromaDB directory
MAX_INGEST_EXAMPLES = 500  # <-- NEW: Max number of examples to ingest

# Create Chroma client with embedding function
chroma_client = chromadb.PersistentClient(path=DB_DIR)
embedding_func = embedding_functions.DefaultEmbeddingFunction()

# Collection for decision memory
collection = chroma_client.get_or_create_collection(
    name="npc_decisions",
    embedding_function=embedding_func
)

# ==============================
# INGEST DATASET INTO VECTOR DB
# ==============================
if len(collection.get()['ids']) == 0:  # only ingest once
    print(f"Ingesting up to {MAX_INGEST_EXAMPLES} samples into ChromaDB...")
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:MAX_INGEST_EXAMPLES]  # <-- LIMIT INGESTION
        for idx, line in enumerate(lines):
            item = json.loads(line)
            prompt = item['prompt']
            completion = item['completion']
            collection.add(
                documents=[prompt],
                metadatas=[{"completion": completion}],
                ids=[f"sample_{idx}"]
            )
    print(f"Ingested {len(lines)} samples.")

# ==============================
# DECISION MANAGER FUNCTION
# ==============================
def get_npc_decision(npc_state: str, top_k: int = 3):
    """
    Given an NPC state (personality, needs, location, memory, nearby objects),
    retrieve similar examples from dataset and query Ollama to get structured decision.
    """
    # Retrieve top examples from Chroma
    results = collection.query(
        query_texts=[npc_state],
        n_results=top_k
    )

    examples = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        examples.append(f"STATE: {doc}\nDECISION: {meta['completion']}")

    examples_text = "\n\n".join(examples)

    # Build prompt
    prompt = f"""
You are an NPC decision-making AI.
Here are some past examples of state → decision:
{examples_text}

Now, decide for this new state:
NPC STATE:
{npc_state}

Respond ONLY with a JSON object:
{{
  "thought": "...",
  "action": "...",
  "target": "...",
  "dialogue": "..."
}}
"""
    # Call Ollama
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response['response']

# ==============================
# EXAMPLE USAGE
# ==============================
if __name__ == "__main__":
    npc_state = (
        "Personality: friendly, ambitious. "
        "Needs: {'hunger':85, 'social':60}. "
        "Location: park. "
        "Past memory: 'Had coffee with Alice yesterday'. "
        "Nearby: food stall, Alice."
    )

    decision = get_npc_decision(npc_state)
    print("NPC Decision:", decision)
