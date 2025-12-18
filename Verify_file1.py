import os
import django

# 1. Setup Django Environment (Required to use your models/settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Agent_Powered_Resume_Analyzer.settings')
django.setup()

# 2. Import your Milestone 2 Modules
from core.ai.agent import GeminiAgent
from core.ai.vector_store import VectorStoreManager
from core.ai.parser import chunk_text


def test_ai_logic():
    print("--- 🧪 STARTING MILESTONE 2 VERIFICATION ---")

    # --- Test 1: Gemini Connection ---
    print("\n1. Testing Gemini Agent Connection...")
    try:
        agent = GeminiAgent()
        print("   ✅ Gemini Client Initialized.")
    except Exception as e:
        print(f"   ❌ Failed to initialize Gemini: {e}")
        return

    # --- Test 2: Embedding Generation ---
    print("\n2. Testing Embedding Generation (text-embedding-004)...")
    test_text = "Software Engineer with 5 years of experience in Python and Django."
    try:
        vector = agent.get_embedding(test_text)
        if len(vector) > 0:
            print(f"   ✅ Embedding generated successfully! Vector length: {len(vector)}")
        else:
            print("   ❌ Embedding returned empty.")
    except Exception as e:
        print(f"   ❌ Embedding Failed: {e}")

    # --- Test 3: Skill Extraction ---
    print("\n3. Testing Skill Extraction (gemini-1.5-flash)...")
    try:
        skills = agent.extract_skills(test_text)
        print(f"   ✅ Raw Skills Extracted: {skills}")
    except Exception as e:

        print(f"   ❌ Skill Extraction Failed: {e}")

    # --- Test 4: Vector Store (ChromaDB) ---
    print("\n4. Testing ChromaDB (Vector Store)...")
    try:
        vs_manager = VectorStoreManager()
        # Create a dummy chunk to add
        chunks = [test_text]
        embeddings = [vector]  # Use the vector we generated in Test 2

        # We use a dummy ID 'test_999'
        vs_manager.add_resume_chunks("test_999", chunks, embeddings)
        print("   ✅ Data added to ChromaDB successfully.")

        # Verify retrieval
        results = vs_manager.search_similar(vector, n_results=1)
        if results['documents'][0]:
            print(f"   ✅ Retrieval Verified: Found document: '{results['documents'][0][0]}'")
        else:
            print("   ❌ Retrieval returned no results.")

    except Exception as e:
        print(f"   ❌ Vector Store Test Failed: {e}")

    print("\n--- 🏁 VERIFICATION COMPLETE ---")


if __name__ == "__main__":
    test_ai_logic()