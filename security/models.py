from django.db import models
from django.conf import settings

class Lab(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g. Lab-A, Lab-B")
    ip_range_start = models.GenericIPAddressField(help_text="Start of IP range")
    ip_range_end = models.GenericIPAddressField(help_text="End of IP range")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class AllowedIP(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='allowed_ips', null=True, blank=True)
    ip_address = models.GenericIPAddressField(unique=True)
    description = models.CharField(max_length=255, help_text="e.g., Lab 1 - System 5")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} ({self.description})"

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
