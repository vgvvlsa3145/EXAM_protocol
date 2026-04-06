from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from security.models import AuditLog
from security.middleware import IPRestrictionMiddleware

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ip = IPRestrictionMiddleware(None).get_client_ip(request)
    AuditLog.objects.create(
        user=user,
        action="Login",
        ip_address=ip,
        details="User logged in successfully."
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    ip = IPRestrictionMiddleware(None).get_client_ip(request)
    AuditLog.objects.create(
        user=user,
        action="Logout",
        ip_address=ip,
        details="User logged out."
    )

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    ip = IPRestrictionMiddleware(None).get_client_ip(request)
    username = credentials.get('username', 'Unknown')
    # We can't log user=... because login failed, so user might not exist or be None
    # AuditLog user field is nullable, so that's fine.
    AuditLog.objects.create(
        action="Login Failed",
        ip_address=ip,
        details=f"Failed login attempt for username: {username}"
    )
