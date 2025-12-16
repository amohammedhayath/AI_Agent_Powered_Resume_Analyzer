from celery import shared_task
from .models import Resume
import time


@shared_task
def process_resume_task(resume_id):
    """
    Background task to process the resume.
    1. Fetch Resume object
    2. Parse File (PDF/DOCX) -> Text
    3. Generate Embeddings & Save to ChromaDB
    4. Update Resume status
    """
    try:
        print(f"Starting processing for Resume ID: {resume_id}")
        resume = Resume.objects.get(id=resume_id)

        # --- LOGIC WILL GO HERE IN MILESTONE 3 ---
        # For now, we simulate processing
        time.sleep(5)

        resume.processing_status = 'INDEXED'
        resume.save()
        print(f"Finished processing for Resume ID: {resume_id}")

    except Resume.DoesNotExist:
        print(f"Resume ID {resume_id} not found.")
    except Exception as e:
        print(f"Error processing resume: {e}")
        if 'resume' in locals():
            resume.processing_status = 'FAILED'
            resume.error_message = str(e)
            resume.save()