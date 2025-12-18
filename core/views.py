from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from .models import Resume, JobDescription
from .serializers import (
    ResumeSerializer, JobDescriptionSerializer,
    MatchResultSerializer, ResumeStatusSerializer
)
# IMPORANT: We import both tasks now
from .tasks import process_resume_task, analyze_job_match_task

# --- 1. Upload Resume (Async Trigger) ---
class ResumeUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            resume = serializer.save()
            # Trigger Celery Task
            process_resume_task.delay(resume.id)
            return Response(
                ResumeStatusSerializer(resume).data,
                status=status.HTTP_202_ACCEPTED
            )

# --- 2. Check Status (Polling) ---
class ResumeStatusView(RetrieveAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeStatusSerializer

# --- 3. Analyze Job (The "Brain" Trigger) ---
class JobAnalyzeView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # 1. Flexible Data Extraction
            # (Allows you to use 'title' OR 'job_title' in Postman)
            title = request.data.get('title') or request.data.get('job_title')
            description = request.data.get('description') or request.data.get('job_description')
            resume_id = request.data.get('resume_id')

            # 2. Validation
            if not all([title, description, resume_id]):
                return Response(
                    {"error": "Missing required fields: resume_id, title/job_title, description"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3. Save Job to DB
            job = JobDescription.objects.create(
                title=title,
                description=description
            )

            # 4. Trigger the AI Agent
            # This sends the job_id and resume_id to Celery
            analyze_job_match_task.delay(job.id, resume_id)

            return Response({
                "message": "Analysis started successfully",
                "job_id": job.id,
                "resume_id": resume_id,
                "status": "PROCESSING"
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from .models import MatchResult

class MatchResultView(APIView):
    def get(self, request, job_id):
        try:
            match = MatchResult.objects.get(job_description_id=job_id)
            return Response({
                "score": match.fitment_score,
                "justification": match.justification,
                "status": "COMPLETED"
            }, status=status.HTTP_200_OK)
        except MatchResult.DoesNotExist:
            return Response({"status": "PENDING"}, status=status.HTTP_200_OK)