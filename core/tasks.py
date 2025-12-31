import os
import json
import chromadb
import google.generativeai as genai
from celery import shared_task
from django.conf import settings
from .models import Resume, JobDescription, MatchResult, OptimizationSuggestion
from dotenv import load_dotenv

load_dotenv()


# --- CONFIGURATION ---
# 1. Get API Key
api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="resume_embeddings")


# --- TASK 1: PROCESS RESUME ---
@shared_task
def process_resume_task(resume_id):
    try:
        print(f"Starting processing for Resume ID: {resume_id}")
        resume = Resume.objects.get(id=resume_id)

        # 1. Extract Data using Gemini
        model = genai.GenerativeModel('gemini-flash-latest')
        # (Assuming file exists and is readable. In prod, use pypdf)
        uploaded_file = genai.upload_file(resume.file.path)

        # Extract Skills
        response = model.generate_content([
            "Extract skills from this resume as a JSON list. Example: ['Python', 'Django']",
            uploaded_file
        ])
        try:
            skills_text = response.text.strip().replace('```json', '').replace('```', '')
            resume.extracted_skills = json.loads(skills_text)
        except:
            resume.extracted_skills = []

        # Extract Text
        text_response = model.generate_content(["Extract full text from this resume.", uploaded_file])
        full_text = text_response.text
        resume.raw_text = full_text

        # 2. Generate Embeddings (The "Brain" Memory)
        chunks = [c for c in full_text.split('\n\n') if c.strip()]
        embedding_model = 'models/text-embedding-004'

        for i, chunk in enumerate(chunks):
            # Create Embedding
            embedding = genai.embed_content(
                model=embedding_model,
                content=chunk,
                task_type="retrieval_document"
            )['embedding']

            # Save to ChromaDB
            collection.add(
                ids=[f"resume_{resume.id}_chunk_{i}"],
                embeddings=[embedding],  # <--- Storing Gemini Vectors
                documents=[chunk],
                metadatas=[{"resume_id": str(resume.id)}]
            )

        resume.vector_store_id = f"resume_{resume.id}"
        resume.processing_status = 'INDEXED'
        resume.save()
        print(f"Resume {resume_id} processed successfully.")

    except Exception as e:
        print(f"Error processing resume: {e}")
        resume = Resume.objects.get(id=resume_id)
        resume.processing_status = 'FAILED'
        resume.save()


# --- TASK 2: ANALYZE JOB MATCH (Fixed) ---
@shared_task
def analyze_job_match_task(job_id, resume_id):
    try:
        print(f"Starting analysis for Job {job_id} vs Resume {resume_id}...")

        # 1. Fetch Data
        job = JobDescription.objects.get(id=job_id)
        resume = Resume.objects.get(id=resume_id)

        if not resume.vector_store_id:
            print("Error: Resume not indexed.")
            return

        # 2. RAG Retrieval (FIXED: Use Gemini Embeddings for Query)
        embedding_model = 'models/text-embedding-004'

        # Convert Job Description to Vector using Gemini
        query_embedding = genai.embed_content(
            model=embedding_model,
            content=job.description,
            task_type="retrieval_query"
        )['embedding']

        # Search ChromaDB using the VECTOR, not the text
        results = collection.query(
            query_embeddings=[query_embedding],  # <--- Comparing Vector to Vector
            n_results=3,
            where={"resume_id": str(resume.id)}
        )

        if not results['documents'][0]:
            print("No relevant chunks found.")
            relevant_chunks = ["No specific match found in resume."]
        else:
            relevant_chunks = results['documents'][0]

        print(f"Found {len(relevant_chunks)} relevant chunks.")

        # 3. AI Analysis
        context_text = "\n".join(relevant_chunks)
        prompt = f"""
        You are an expert HR AI. Compare the following Candidate Context against the Job Description.

        JOB DESCRIPTION:
        {job.description}

        CANDIDATE RELEVANT EXPERIENCE:
        {context_text}

        TASK:
        1. Assign a fitment score (0-100).
        2. Write a 2-sentence justification explaining the score.

        OUTPUT FORMAT (JSON only):
        {{
            "score": 85,
            "justification": "The candidate has..."
        }}
        """

        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)

        json_text = response.text.strip().replace('```json', '').replace('```', '')
        analysis_data = json.loads(json_text)

        # 4. Save Results
        MatchResult.objects.create(
            job_description=job,
            resume=resume,
            fitment_score=analysis_data.get('score'),
            justification=analysis_data.get('justification'),
            relevant_chunks=relevant_chunks
        )

        print(f"Analysis Complete! Score: {analysis_data.get('score')}")
        return "Match Analysis Succeeded"

    except Exception as e:
        print(f"Analysis Failed: {str(e)}")
        return f"Failed: {str(e)}"

# --- TASK 3: GENERATE OPTIMIZATION SUGGESTIONS ---
@shared_task
def generate_optimization_task(match_id):
    try:
        print(f"Starting Optimization for Match ID: {match_id}")
        match = MatchResult.objects.get(id=match_id)
        job = match.job_description
        resume = match.resume

        # 1. Construct the Context-Aware Prompt
        # We give the AI the specific chunks relevant to the job, not the whole resume (to save tokens/focus)
        resume_context = "\n".join(match.relevant_chunks)

        prompt = f"""
        Act as an Expert Technical Resume Writer. Your goal is "Semantic Alignment."
        
        CONTEXT:
        A candidate applied for a job but used generic terms. You must rewrite their bullet points to use the specific professional terminology found in the Job Description, without inventing new skills.

        JOB DESCRIPTION:
        {job.description}

        CANDIDATE'S CURRENT RESUME SNIPPETS:
        {resume_context}

        TASK:
        Identify 3 specific bullet points or sentences from the Candidate's snippets that can be improved.
        For each, rewrite it to adopt the specific vocabulary/keywords from the Job Description.
        
        RULES:
        1. Do NOT invent skills the candidate didn't mention.
        2. Keep the rewritten version concise and professional.
        3. Explain strictly WHY you changed it (e.g., "Mapped generic 'database' to specific 'PostgreSQL' from JD").

        OUTPUT FORMAT (Strict JSON List):
        [
            {{
                "original_text": "text from resume",
                "optimized_text": "rewritten text with JD keywords",
                "reason": "explanation",
                "category": "Terminology"
            }}
        ]
        """

        # 2. Call Gemini
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)

        # 3. Clean JSON
        json_text = response.text.strip().replace('```json', '').replace('```', '')
        suggestions = json.loads(json_text)

        # 4. Save to Database
        # Clear old suggestions for this match first (optional)
        OptimizationSuggestion.objects.filter(match_result=match).delete()

        for item in suggestions:
            OptimizationSuggestion.objects.create(
                match_result=match,
                original_text=item.get('original_text'),
                optimized_text=item.get('optimized_text'),
                reason=item.get('reason'),
                category=item.get('category', 'Terminology')
            )
        
        print(f"Optimization Complete. Saved {len(suggestions)} suggestions.")
        return "Optimization Succeeded"

    except Exception as e:
        print(f"Optimization Failed: {str(e)}")
        return f"Failed: {str(e)}"