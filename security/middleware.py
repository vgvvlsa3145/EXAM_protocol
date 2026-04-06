import logging
import ipaddress
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from .models import AllowedIP, Lab
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class IPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip static and media files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
             return self.get_response(request)
        
        ip_str = self.get_client_ip(request)
        
        # 1. ALLOWED BYPASS (Localhost/Admin)
        if ip_str in ['127.0.0.1', 'localhost', '::1']:
             return self.get_response(request)

        if getattr(settings, 'ALLOW_ALL_IPS', False):
            return self.get_response(request)

        # 2. CHECK ALLOWED INDIVIDUAL IPS
        cache_key = f'allowed_ip_{ip_str}'
        is_allowed = cache.get(cache_key)

        if is_allowed is None:
            is_allowed = AllowedIP.objects.filter(ip_address=ip_str, is_active=True).exists()
            
            # 3. CHECK LAB IP RANGES (If not already found in Individual IPs)
            if not is_allowed:
                try:
                    client_ip = ipaddress.ip_address(ip_str)
                    labs = Lab.objects.filter(is_active=True)
                    for lab in labs:
                        start = ipaddress.ip_address(lab.ip_range_start)
                        end = ipaddress.ip_address(lab.ip_range_end)
                        if start <= client_ip <= end:
                            is_allowed = True
                            break
                except ValueError:
                    is_allowed = False
                    
            cache.set(cache_key, is_allowed, 30) # Cache for 30s

        if not is_allowed:
            return HttpResponseForbidden(content=f"<h1>Access Denied</h1><p>Your IP ({ip_str}) is not authorized for THIS LAB NETWORK.</p>")

        # 4. EXAM-LAB ENFORCEMENT (Optional extra security)
        # If user is trying to 'take' an exam, check if they are in an allowed lab for that exam
        if request.user.is_authenticated and '/exams/take/' in request.path:
            try:
                # Extract exam ID from URL /exams/take/1/
                parts = request.path.split('/')
                exam_id = [p for p in parts if p.isdigit()][0]
                from exams.models import Exam
                exam = Exam.objects.get(id=exam_id)
                
                # If exam is restricted to specific labs
                allowed_labs = exam.labs.all()
                if allowed_labs.exists():
                    client_ip = ipaddress.ip_address(ip_str)
                    in_correct_lab = False
                    for lab in allowed_labs:
                        if ipaddress.ip_address(lab.ip_range_start) <= client_ip <= ipaddress.ip_address(lab.ip_range_end):
                            in_correct_lab = True
                            break
                    if not in_correct_lab:
                         return HttpResponseForbidden(content=f"<h1>Lab Restriction</h1><p>This exam is restricted to specific labs (e.g. {', '.join([l.name for l in allowed_labs])}). You are not in an authorized lab for this test.</p>")
            except:
                pass

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LoginApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Skip checks for unauthenticated users, Admins, Faculty, or static/media
        if not request.user.is_authenticated or not request.user.role == 'STUDENT' or \
           request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # 2. Skip checks for the waiting page and logout
        exempt_urls = ['/waiting-approval/', '/api/check-approval/', '/logout/', '/login/']
        if any(request.path.startswith(url) for url in exempt_urls) or request.path == '/':
            return self.get_response(request)

        # 3. Check for APPROVED request (must be the MOST RECENT request)
        from accounts.models import LoginRequest
        latest_request = LoginRequest.objects.filter(user=request.user).order_by('-created_at').first()
        
        if latest_request and latest_request.status == 'APPROVED':
            return self.get_response(request)

        # If not approved, force to the waiting page
        from django.shortcuts import redirect
        return redirect('waiting_approval')
