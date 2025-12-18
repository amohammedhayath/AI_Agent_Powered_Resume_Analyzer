from django.urls import path
from .views import ResumeUploadView, ResumeStatusView, JobAnalyzeView, MatchResultView
urlpatterns = [
    path('resumes/', ResumeUploadView.as_view(), name='resume-upload'),
    path('resumes/<int:pk>/status/', ResumeStatusView.as_view(), name='resume-status'),
    path('jobs/analyze/', JobAnalyzeView.as_view(), name='job-analyze'),
    path('jobs/<int:job_id>/result/', MatchResultView.as_view(), name='match-result'),
]