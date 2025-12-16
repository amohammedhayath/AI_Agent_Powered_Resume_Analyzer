from django.urls import path
from .views import ResumeUploadView, ResumeStatusView, JobAnalysisView

urlpatterns = [
    path('resumes/', ResumeUploadView.as_view(), name='resume-upload'),
    path('resumes/<int:pk>/status/', ResumeStatusView.as_view(), name='resume-status'),
    path('jobs/analyze/', JobAnalysisView.as_view(), name='job-analyze'),
]