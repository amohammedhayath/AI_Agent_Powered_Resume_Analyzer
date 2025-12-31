# core/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Resume, JobDescription, MatchResult, OptimizationSuggestion
from .serializers import (
    ResumeSerializer, 
    MatchResultSerializer, 
    OptimizationSuggestionSerializer
)
# We import the Async Tasks
from .tasks import process_resume_task, analyze_job_match_task, generate_optimization_task

# --- 1. Upload Resume ---
class ResumeUploadView(APIView):
    def post(self, request):
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            resume = serializer.save()
            # Trigger Celery Task to process PDF
            process_resume_task.delay(resume.id)
            return Response({"id": resume.id, "message": "Upload successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 2. Job Analysis (RENAMED TO MATCH URLS) ---
class JobAnalysisView(APIView):
    def post(self, request):
        resume_id = request.data.get('resume_id')
        title = request.data.get('title', 'General Role')
        description = request.data.get('description')

        if not resume_id or not description:
            return Response({"error": "Resume ID and Job Description are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create Job Record
        job = JobDescription.objects.create(
            title=title,
            description=description
        )

        # Trigger Celery Task for Analysis
        analyze_job_match_task.delay(job.id, resume_id)

        return Response({
            "job_id": job.id, 
            "status": "PROCESSING"
        }, status=status.HTTP_202_ACCEPTED)

# --- 3. Match Result ---
class MatchResultView(APIView):
    def get(self, request, job_id):
        try:
            match = MatchResult.objects.get(job_description_id=job_id)
            return Response({
                "match_id": match.id,
                "score": match.fitment_score,
                "justification": match.justification,
                "status": "COMPLETED"
            }, status=status.HTTP_200_OK)
        except MatchResult.DoesNotExist:
            return Response({"status": "PENDING"}, status=status.HTTP_200_OK)

# --- 4. Optimization Trigger ---
class TriggerOptimizationView(APIView):
    def post(self, request):
        match_id = request.data.get('match_id')
        if not match_id:
            return Response({"error": "match_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Trigger Celery Task
        generate_optimization_task.delay(match_id)
        
        return Response({"message": "Optimization started", "status": "PROCESSING"}, status=status.HTTP_202_ACCEPTED)

# --- 5. Optimization Result ---
class OptimizationResultView(APIView):
    def get(self, request, match_id):
        suggestions = OptimizationSuggestion.objects.filter(match_result_id=match_id)
        
        if not suggestions.exists():
             return Response({"status": "PENDING", "data": []}, status=status.HTTP_200_OK)
        
        serializer = OptimizationSuggestionSerializer(suggestions, many=True)
        return Response({
            "status": "COMPLETED", 
            "data": serializer.data
        }, status=status.HTTP_200_OK)