from django.urls import path
from . import views

urlpatterns = [
    path('marks-analysis/', views.marks_analysis, name='marks_analysis'),
    path('export-analysis/', views.export_analysis_csv, name='export_analysis_csv'),
    path('live-monitoring/', views.live_monitoring, name='live_monitoring'),
    path('attempt-detail/<int:attempt_id>/', views.student_attempt_detail, name='student_attempt_detail'),
]
