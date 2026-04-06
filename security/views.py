from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from .models import AuditLog

@login_required
def heartbeat(request):
    """
    Updates the user's last_seen timestamp in the cache/session.
    Since we don't have a specific field, we'll use the Profile or a simple cache key.
    For simplicity in this file-based setup, we'll update the User's last_login 
    (or we could use a custom cache, but let's stick to DB for persistence).
    Actually, frequent DB updates are bad, but for < 100 users, it's fine.
    """
    user = request.user
    # We will use the built-in last_login field as 'last_seen' for this purpose
    # To avoid Logout issues, we only update if it's been > 30 seconds? 
    # No, let's just update it.
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    return JsonResponse({'status': 'ok'})

@login_required
def get_live_logs(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    # Get last 20 logs
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:20]
    data = []
    for log in logs:
        user_str = log.user.username if log.user else "System/Unknown"
        local_time = timezone.localtime(log.timestamp)
        data.append({
            'timestamp': local_time.strftime('%b %d, %I:%M:%S %p'),
            'date': local_time.strftime('%Y-%m-%d'),
            'user': user_str,
            'action': log.action,
            'ip': log.ip_address,
            'details': log.details
        })
    return JsonResponse({'logs': data})

@login_required
def log_violation(request, exam_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
    import json
    try:
        data = json.loads(request.body)
        action = data.get('action', 'Security Violation')
        details = data.get('details', '')
    except:
        return JsonResponse({'error': 'Invalid data'}, status=400)
        
    from exams.models import Exam, StudentExamAttempt
    exam = Exam.objects.get(id=exam_id)
    attempt = StudentExamAttempt.objects.filter(student=request.user, exam=exam, status='IN_PROGRESS').first()
    
    if attempt:
        # Increment violation count
        attempt.violation_count += 1
        attempt.save(update_fields=['violation_count'])
        
        # Log to AuditLog
        AuditLog.objects.create(
            user=request.user,
            action=f"EXAM VIOLATION: {action}",
            ip_address=request.META.get('REMOTE_ADDR'),
            details=f"Violation #{attempt.violation_count} during exam '{exam.title}': {details}"
        )
        
        return JsonResponse({'status': 'ok', 'count': attempt.violation_count})
    
    return JsonResponse({'error': 'No active attempt found'}, status=404)

@login_required
def system_diagnostics(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    import psutil
    import time
    from django.contrib.sessions.models import Session
    from django.db import connection
    
    # 1. CPU & RAM
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    # 2. Active Sessions (Online Users - Last 5 mins)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # We use last_login as a proxy for "last seen" because heartbeat updates it
    five_min_ago = timezone.now() - timezone.timedelta(minutes=5)
    active_sessions = User.objects.filter(last_login__gte=five_min_ago).count()
    
    # 3. DB Health Check (Simple query execution time)
    start_db = time.time()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    db_latency = (time.time() - start_db) * 1000 # ms
    
    return JsonResponse({
        'cpu': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used_gb': round(memory.used / (1024**3), 2),
        'active_sessions': active_sessions,
        'db_latency': round(db_latency, 2),
        'timestamp': timezone.localtime(timezone.now()).strftime('%H:%M:%S')
    })

@login_required
def export_backup(request):
    if not (request.user.is_staff or request.user.role == 'ADMIN'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    import zipfile
    import io
    import os
    from django.http import HttpResponse
    from django.conf import settings
    
    # Create a zip in memory
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        # 1. Add DB
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            zf.write(db_path, arcname='db.sqlite3')
            
        # 2. Add Media files (if media folder exists)
        if os.path.exists(settings.MEDIA_ROOT):
            for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, arcname=os.path.relpath(file_path, settings.BASE_DIR))
                
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="EXAM_BACKUP_{timestamp}.zip"'
    return response

@login_required
def restore_backup(request):
    if not (request.user.is_staff or request.user.role == 'ADMIN'):
        from django.contrib import messages
        messages.error(request, "Unauthorized.")
        return redirect('admin_dashboard')
        
    if request.method == 'POST' and request.FILES.get('backup_file'):
        import zipfile
        import shutil
        import os
        from django.conf import settings
        from django.shortcuts import redirect
        from django.contrib import messages
        
        backup_zip = request.FILES['backup_file']
        temp_dir = os.path.join(settings.BASE_DIR, 'temp_restore')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(backup_zip, 'r') as zf:
                zf.extractall(temp_dir)
                
            # Overwrite DB
            new_db_path = os.path.join(temp_dir, 'db.sqlite3')
            if os.path.exists(new_db_path):
                # Using copy2 to preserve metadata, overwriting existing db
                shutil.copy2(new_db_path, settings.DATABASES['default']['NAME'])
                messages.success(request, "System state restored successfully. Logging in again may be required.")
            else:
                messages.warning(request, "No database file found in the backup zip.")
                
            # Cleanup
            shutil.rmtree(temp_dir)
        except Exception as e:
            messages.error(request, f"Restore failed: {str(e)}")
            
    return redirect('admin_dashboard')


