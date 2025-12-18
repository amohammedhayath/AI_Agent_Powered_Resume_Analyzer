from django.contrib import admin
from .models import Resume, JobDescription, MatchResult

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate_name', 'processing_status', 'date_uploaded')
    list_filter = ('processing_status',)
    search_fields = ('candidate_name', 'raw_text')
    readonly_fields = ('id', 'date_uploaded', 'vector_store_id')

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_analyzed')
    readonly_fields = ('date_analyzed',)

@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('resume', 'job_description', 'fitment_score')
    readonly_fields = ('fitment_score', 'justification', 'relevant_chunks')