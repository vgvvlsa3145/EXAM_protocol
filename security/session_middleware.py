from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from .models import AuditLog

class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if the user's current DB session key matches their request's session key
            db_session = request.user.current_session_key
            current_session = request.session.session_key
            
            if db_session and current_session and db_session != current_session:
                # Log the security event
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
                
                AuditLog.objects.create(
                    user=request.user,
                    action="Multiple Login Attempt",
                    ip_address=ip,
                    details="Session invalidated. User logged in from another device."
                )
                
                logout(request)
                messages.error(request, "You have been logged out because this account was accessed from another device.")
                return redirect('login')
                
        response = self.get_response(request)
        return response
