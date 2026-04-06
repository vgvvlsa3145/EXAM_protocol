from django.contrib import admin
from .models import AllowedIP, AuditLog, Lab

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_range_start', 'ip_range_end', 'is_active')
    list_filter = ('is_active',)

@admin.register(AllowedIP)
class AllowedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'lab', 'description', 'is_active')
    list_filter = ('lab', 'is_active')
    search_fields = ('ip_address', 'description')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'ip_address', 'details')
