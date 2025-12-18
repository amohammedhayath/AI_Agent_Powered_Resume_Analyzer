# 🚀 AI Agent-Powered Resume Analyzer

A Full-Stack AI Application that uses **Google Gemini**, **RAG (Retrieval-Augmented Generation)**, and **Agentic Workflows** to analyze resumes against job descriptions.

## 🌟 Features
- **AI Agent:** "Reads" PDFs and understands context (not just keywords).
- **RAG Engine:** Uses ChromaDB to perform semantic searches on candidate experience.
- **Async Processing:** Celery + Redis handles heavy AI tasks in the background.
- **Fitment Score:** Generates a 0-100% score with a detailed "Verdict" justification.
- **Modern Stack:** React Frontend + Django REST API.

## 🛠️ Tech Stack
- **Frontend:** React.js, Bootstrap, Axios
- **Backend:** Django REST Framework, Python
- **AI/ML:** Google Gemini 1.5 Flash, ChromaDB (Vector Store)
- **Task Queue:** Celery, Redis

## 🚀 How to Run
1. **Backend:**
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   celery -A AI_Agent_Powered_Resume_Analyzer worker --pool=solo
   python manage.py runserver
   
2. **Frontend:**
    ```Bash
    cd resume-ai-frontend
    npm install
    npm start