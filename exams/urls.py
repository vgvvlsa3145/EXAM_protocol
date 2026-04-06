from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructions/<int:exam_id>/', views.exam_instructions, name='exam_instructions'),
    path('take/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('submit/<int:exam_id>/', views.submit_exam, name='submit_exam'),
    path('reset-attempt/<int:attempt_id>/', views.reset_attempt, name='reset_attempt'),
    path('publish-results/<int:exam_id>/', views.publish_results, name='publish_results'),
    path('export-results/<int:exam_id>/', views.export_results_csv, name='export_results_csv'),
    path('result/<int:attempt_id>/', views.view_result, name='view_result'),
    path('force-submit/<int:attempt_id>/', views.force_submit_attempt, name='force_submit_attempt'),
    path('autosave/<int:exam_id>/', views.autosave_exam, name='autosave_exam'),
    path('check-status/<int:exam_id>/', views.check_exam_status, name='check_status'),
    path('api/announcements/', views.get_active_announcements, name='get_active_announcements'),
]
