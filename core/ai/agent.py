import os
import json
from google.genai import Client
from google.genai import types
from django.conf import settings


class GeminiAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        self.client = Client(api_key=self.api_key)

    def get_embedding(self, text):
        try:
            response = self.client.models.embed_content(
                model='text-embedding-004',
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def extract_skills(self, resume_text):
        prompt = """
        You are an expert Resume Parser. 
        Extract all technical skills, tools, and soft skills from the following resume text.
        Return ONLY a raw JSON list of strings. Do not include markdown formatting.

        Resume Text:
        {text}
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt.format(text=resume_text[:10000]),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return []