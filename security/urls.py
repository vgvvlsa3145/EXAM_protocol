from django.urls import path
from . import views

urlpatterns = [
    path('api/logs/', views.get_live_logs, name='get_live_logs'),
    path('heartbeat/', views.heartbeat, name='heartbeat'),
    path('log-violation/<int:exam_id>/', views.log_violation, name='log_violation'),
    path('api/diagnostics/', views.system_diagnostics, name='system_diagnostics'),
    path('backup/export/', views.export_backup, name='export_backup'),
    path('backup/restore/', views.restore_backup, name='restore_backup'),
]
