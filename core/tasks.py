from celery import shared_task
from .models import Resume

# --- UPDATED IMPORTS ---
# Notice we now import from .ai.package_name
from .ai.parser import parse_resume, chunk_text
from .ai.agent import GeminiAgent
from .ai.vector_store import VectorStoreManager


@shared_task
def process_resume_task(resume_id):
    try:
        print(f"Starting processing for Resume ID: {resume_id}")
        resume = Resume.objects.get(id=resume_id)

        # 1. Parse File
        # resume.file.path gives the absolute path on disk
        full_text = parse_resume(resume.file.path)
        if not full_text:
            raise ValueError("Could not extract text from file.")

        # Save raw text to DB
        resume.raw_text = full_text
        resume.save()

        # 2. Extract Skills (Gemini)
        agent = GeminiAgent()
        skills = agent.extract_skills(full_text)
        resume.extracted_skills = skills
        resume.save()

        # 3. Chunk & Embed
        chunks = chunk_text(full_text)
        embeddings = []
        for chunk in chunks:
            # Generate embedding for each chunk
            vector = agent.get_embedding(chunk)
            embeddings.append(vector)

        # 4. Save to ChromaDB
        vector_manager = VectorStoreManager()
        vector_manager.add_resume_chunks(resume_id, chunks, embeddings)

        # Save reference ID
        resume.vector_store_id = f"resume_{resume_id}"

        # 5. Success!
        resume.processing_status = 'INDEXED'
        resume.save()
        print(f"Finished processing for Resume ID: {resume_id}")

    except Resume.DoesNotExist:
        print(f"Resume ID {resume_id} not found.")
    except Exception as e:
        print(f"Error processing resume: {e}")
        # Re-fetch in case connection closed
        try:
            resume = Resume.objects.get(id=resume_id)
            resume.processing_status = 'FAILED'
            resume.error_message = str(e)
            resume.save()
        except:
            pass