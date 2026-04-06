from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import User, LoginRequest
from .utils import get_mac_address
from security.middleware import IPRestrictionMiddleware

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # LOGIN APPROVAL LOGIC
            if user.role == 'STUDENT':
                # Create login request, then log them in, BUT middleware will block them
                ip = IPRestrictionMiddleware(None).get_client_ip(request)
                mac = get_mac_address(ip)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                from .utils import get_platform_info
                platform, device = get_platform_info(user_agent)
                
                LoginRequest.objects.create(
                    user=user,
                    ip_address=ip,
                    mac_address=mac,
                    platform=platform,
                    device_info=device,
                    user_agent=user_agent,
                    status='PENDING'
                )
                
                login(request, user)
                return redirect('waiting_approval')
            
            # Admin/Faculty bypass approval
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def waiting_approval(request):
    if not request.user.role == 'STUDENT':
        return redirect('dashboard')
    # Get the absolutly most recent login request
    latest_req = LoginRequest.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not latest_req:
        # Failsafe if they got here without a request
        return redirect('login')

    # Check if they have an APPROVED request currently
    if latest_req.status == 'APPROVED':
        return redirect('student_dashboard')
        
    # Check if REJECTED
    if latest_req.status == 'REJECTED':
        logout(request)
        messages.error(request, "Your login request was rejected by the admin.")
        return redirect('login')

    return render(request, 'accounts/waiting_approval.html')

@login_required
def check_approval_api(request):
    """
    Called via AJAX from waiting_approval.html to auto-redirect when approved.
    """
    status = 'PENDING'
    req = LoginRequest.objects.filter(user=request.user).order_by('-created_at').first()
    if req:
        status = req.status
        
    return JsonResponse({'status': status})

@login_required
def approve_login(request, request_id):
    """
    Consolidated approval view for both standard and passwordless logins.
    Generates a login token for passwordless and sets status to APPROVED.
    """
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    login_req = get_object_or_404(LoginRequest, id=request_id)
    
    import uuid
    login_req.status = 'APPROVED'
    login_req.login_token = str(uuid.uuid4()) # Essential for passwordless redirection
    login_req.save()
    
    from security.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action="Login Approved",
        details=f"Approved login for {login_req.user.username}",
        ip_address=IPRestrictionMiddleware(None).get_client_ip(request)
    )
    
    messages.success(request, f"Approved login for {login_req.user.username}")
    
    # Redirect back to where they came from
    next_url = request.GET.get('next', 'admin_dashboard')
    if next_url == 'pending_logins':
         return redirect('admin_list_login_requests')
    return redirect('admin_dashboard')

def request_passwordless_login(request):
    """
    AJAX view to request login access without a password.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        username = data.get('username')
        
        user = User.objects.filter(username=username, role='STUDENT').first()
        if not user:
            return JsonResponse({'success': False, 'message': 'Invalid registration ID.'}, status=404)
            
        # Create the request
        ip = IPRestrictionMiddleware(None).get_client_ip(request)
        from .utils import get_platform_info
        platform, device = get_platform_info(request.META.get('HTTP_USER_AGENT', ''))
        
        # Cancel any previous pending requests for this user
        LoginRequest.objects.filter(user=user, status='PENDING').update(status='REJECTED')
        
        # 6-digit OTP generation
        import random
        otp = str(random.randint(100000, 999999))
        
        login_req = LoginRequest.objects.create(
            user=user,
            ip_address=ip,
            platform=platform,
            device_info=device,
            status='PENDING',
            otp=otp
        )
        
        return JsonResponse({'success': True, 'request_id': login_req.id})
    return JsonResponse({'success': False}, status=405)

def verify_passwordless_otp(request):
    """
    Validates the OTP entered by the student and logs them in.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        request_id = data.get('request_id')
        otp = data.get('otp')
        
        login_req = LoginRequest.objects.filter(id=request_id, status='APPROVED').first()
        if not login_req:
            return JsonResponse({'success': False, 'message': 'Request not approved or expired.'}, status=403)
            
        if login_req.otp == otp:
            # OTP match! Log them in.
            login(request, login_req.user)
            login_req.otp = None # Clear OTP
            login_req.save()
            return JsonResponse({'success': True, 'redirect': '/'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid OTP. Please check with your Admin.'}, status=401)
            
    return JsonResponse({'success': False}, status=405)

def check_passwordless_status(request, request_id):
    """
    Polls for approval. Returns token if approved.
    """
    login_req = get_object_or_404(LoginRequest, id=request_id)
    if login_req.status == 'APPROVED' and login_req.login_token:
        return JsonResponse({'status': 'APPROVED', 'token': login_req.login_token})
    return JsonResponse({'status': login_req.status})

def login_with_token(request, token):
    """
    Actual login view using a one-time token.
    """
    login_req = LoginRequest.objects.filter(login_token=token, status='APPROVED').first()
    if not login_req:
        messages.error(request, "Invalid or expired login token.")
        return redirect('login')
        
    # Valid token found. Log them in.
    login(request, login_req.user)
    
    # Invalidate token
    login_req.login_token = None
    login_req.save()
    
    return redirect('dashboard')

@login_required
def admin_list_login_requests(request):
    """
    View for admin to see and manage login requests.
    """
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    pending_requests = LoginRequest.objects.filter(status='PENDING').order_by('-created_at')
    return render(request, 'accounts/pending_logins.html', {'requests': pending_requests})

@login_required
def admin_approve_request(request, request_id):
    """
    Admin approves a login request and generates a token or OTP.
    """
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    login_req = get_object_or_404(LoginRequest, id=request_id)
    import uuid
    login_req.status = 'APPROVED'
    login_req.login_token = str(uuid.uuid4())
    login_req.save()
    
    # Create audit log
    from security.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action="Passwordless Login Approved",
        details=f"Approved passwordless login for {login_req.user.username}",
        ip_address=IPRestrictionMiddleware(None).get_client_ip(request)
    )
    
    return redirect('admin_list_login_requests')

@login_required
def reject_login(request, request_id):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    login_req = get_object_or_404(LoginRequest, id=request_id)
    login_req.status = 'REJECTED'
    login_req.save()
    
    messages.warning(request, f"Rejected login for {login_req.user.username}")
    return redirect('admin_dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'STUDENT':
        return redirect('student_dashboard')
    elif user.role == 'FACULTY':
        # For now, faculty shares the admin dashboard or has a similar one
        return redirect('admin_dashboard')
    elif user.role == 'ADMIN' or user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('login')

@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    from accounts.models import User
    from exams.models import Exam, StudentExamAttempt
    from security.models import AuditLog
    
    from django.utils import timezone
    from django.db.models.functions import TruncDate
    now = timezone.now()
    
    import json
    # Get distinct dates where exams were actually attempted
    attempt_dates = list(StudentExamAttempt.objects.annotate(
        date=TruncDate('start_time')
    ).values_list('date', flat=True).distinct())
    attempt_dates_str = json.dumps([d.strftime('%Y-%m-%d') for d in attempt_dates if d])
    
    context = {
        'total_students': User.objects.filter(role='STUDENT').count(),
        'active_exams': Exam.objects.filter(is_active=True, start_time__lte=now, end_time__gte=now).count(),
        'total_attempts': StudentExamAttempt.objects.count(),
        'recent_logs': AuditLog.objects.order_by('-timestamp')[:5],
        'recent_attempts': StudentExamAttempt.objects.order_by('-start_time')[:50],
        'all_exams': Exam.objects.all().order_by('-start_time'),
        'all_users': User.objects.filter(role='STUDENT', last_login__gte=now - timezone.timedelta(minutes=10)).order_by('-last_login'), 
        'pending_logins': LoginRequest.objects.filter(status='PENDING').order_by('-created_at'),
        'available_dates_json': attempt_dates_str,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def student_detail_view(request, student_id=None):
    from django.shortcuts import get_object_or_404
    from .models import User, StudentProfile
    from exams.models import StudentExamAttempt
    from security.models import AuditLog

    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    student = None
    if student_id:
        student = get_object_or_404(User, id=student_id, role='STUDENT')
    else:
        # Handling Search
        query = request.GET.get('q')
        if query:
            # Enhanced Search Logic
            search_filter = (
                Q(username__icontains=query) |
                Q(student_profile__roll_number__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
            
            # Find matching students
            matches = User.objects.filter(search_filter, role='STUDENT').distinct()
            count = matches.count()
            
            if count == 1:
                student = matches.first()
            elif count > 1:
                # Multiple matches found, redirect to manage users (search view)
                return redirect(f'/accounts/manage-users/?q={query}')
            else:
                messages.error(request, f"No student found matching: {query}")
                return redirect('admin_dashboard')
        else:
             return redirect('admin_dashboard')

    # Fetch 360 Data
    profile = getattr(student, 'student_profile', None)
    attempts = StudentExamAttempt.objects.filter(student=student).order_by('-start_time')
    logs = AuditLog.objects.filter(user=student).order_by('-timestamp')
    
    context = {
        'student': student,
        'profile': profile,
        'attempts': attempts,
        'logs': logs
    }
    return render(request, 'accounts/student_detail.html', context)

@login_required
def manage_users(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
    
    from .models import User
    
    query = request.GET.get('q')
    if query:
        search_filter = (
            Q(username__icontains=query) |
            Q(student_profile__roll_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        users = User.objects.filter(search_filter).distinct()
    else:
        users = User.objects.filter(role__in=['STUDENT', 'FACULTY']).order_by('-date_joined')
        
    return render(request, 'accounts/manage_users.html', {'users': users, 'query': query})

@login_required
def create_student(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
    
    from .forms import StudentCreationForm
    
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Student '{user.username}' created successfully!")
            return redirect('manage_users')
    else:
        form = StudentCreationForm()
        
    return render(request, 'accounts/create_student.html', {'form': form})

@login_required
def admin_password_reset(request, user_id):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    from .models import User
    from .forms import AdminPasswordResetForm
    from django.shortcuts import get_object_or_404
    
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminPasswordResetForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Password for '{target_user.username}' has been reset.")
            return redirect('manage_users')
    else:
        form = AdminPasswordResetForm(target_user)
        
    return render(request, 'accounts/admin_password_reset.html', {'form': form, 'target_user': target_user})

@login_required
def search_students_api(request):
    """
    API for autocomplete search in admin dashboard.
    Returns JSON list of matching students.
    """
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return JsonResponse({'results': []})
        
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
        
    from .models import User
    from django.db.models import Q
    
    search_filter = (
        Q(username__icontains=query) |
        Q(student_profile__roll_number__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )
    
    users = User.objects.filter(search_filter, role='STUDENT').distinct()[:10] # Limit to 10
    
    results = []
    for user in users:
        # Format: "Name (Roll No)"
        try:
            roll = user.student_profile.roll_number
        except:
            roll = 'N/A'
            
        name = user.get_full_name() or user.username
        label = f"{name} ({roll})"
        results.append({
            'id': user.id,
            'label': label,
            'value': roll # When selected, use roll number? Or username? Let's use roll number for search box
        })
        
    return JsonResponse({'results': results})

@login_required
def student_profile_view(request):
    """
    View for students to see their own profile details.
    """
    if not request.user.role == 'STUDENT':
        return redirect('dashboard')
        
    student = request.user
    # Ensure profile exists
    profile = getattr(student, 'student_profile', None)
    
    from exams.models import StudentExamAttempt
    attempts = StudentExamAttempt.objects.filter(student=student).order_by('-submit_time')
    
    context = {
        'student': student,
        'profile': profile,
        'attempts': attempts
    }
    return render(request, 'accounts/student_profile.html', context)
@login_required
def admin_logout_user(request, user_id):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    target_user = get_object_or_404(User, id=user_id)
    
    # Remote logout: Clear the session key in the DB.
    # The SingleSessionMiddleware will detect this mismatch and log them out.
    target_user.current_session_key = 'LOGOUT'
    target_user.save(update_fields=['current_session_key'])
    
    from security.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action="Remote Logout",
        ip_address=request.META.get('REMOTE_ADDR'),
        details=f"Admin remotely logged out student: {target_user.username}"
    )
    
    messages.success(request, f"User {target_user.username} has been remotely logged out.")
    return redirect('admin_dashboard')
@login_required
def admin_logout_all_students(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
    
    # Remote logout all students: Set session key to 'LOGOUT' for everyone with STUDENT role.
    updated = User.objects.filter(role='STUDENT').update(current_session_key='LOGOUT')
    
    from security.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action="Bulk Remote Logout",
        ip_address=request.META.get('REMOTE_ADDR'),
        details=f"Admin remotely logged out ALL ({updated}) students."
    )
    
    messages.success(request, f"Successfully logged out all {updated} students.")
    return redirect('admin_dashboard')
