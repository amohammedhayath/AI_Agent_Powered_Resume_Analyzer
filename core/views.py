from django.shortcuts import render

# Create your views here.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from .models import Resume
from .serializers import (
    ResumeSerializer, JobDescriptionSerializer,
    MatchResultSerializer, ResumeStatusSerializer
)
from .tasks import process_resume_task


# --- 1. Upload Resume (Async Trigger) ---
class ResumeUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            resume = serializer.save()

            # Trigger Celery Task
            process_resume_task.delay(resume.id)

            # Return immediate response
            return Response(
                ResumeStatusSerializer(resume).data,
                status=status.HTTP_202_ACCEPTED
            )


# --- 2. Check Status (Polling) ---
class ResumeStatusView(RetrieveAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeStatusSerializer


# --- 3. Analyze Job (Synchronous Placeholder) ---
class JobAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        jd_serializer = JobDescriptionSerializer(data=request.data)
        if jd_serializer.is_valid(raise_exception=True):
            jd_serializer.save()

            # Placeholder for Matching Engine (Milestone 4)
            return Response([], status=status.HTTP_200_OK)