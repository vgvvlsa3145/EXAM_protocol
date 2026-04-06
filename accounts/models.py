from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import logging
# Avoid circular import by import audit log inside signal


class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    current_session_key = models.CharField(max_length=40, blank=True, null=True)
    
    def is_student(self):
        return self.role == 'STUDENT'
    
    def is_faculty(self):
        return self.role == 'FACULTY'
    
    def is_admin_role(self):
        return self.role == 'ADMIN'

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    year = models.IntegerField(default=1)
    college_name = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"

class LoginRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=50, blank=True, null=True)
    platform = models.CharField(max_length=100, blank=True, null=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    otp = models.CharField(max_length=10, blank=True, null=True)
    login_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} ({self.ip_address})"

# Signal to handle single session
@receiver(user_logged_in)
def enforce_single_session(sender, user, request, **kwargs):
    if request.session.session_key:
        # Kick out old session? Or block new?
        # Standard: Update DB with NEW key. Middleware will check DB vs Request. 
        # If they match, good. If DB has changed (by new login), old request fails.
        user.current_session_key = request.session.session_key
        user.save(update_fields=['current_session_key'])
        
        # Log it?
        # For now, just logging the login event is handled by other generic logs or can be added here.
        # But the actual "Block" happens when the OLD session tries to do something.

