from django.contrib import admin
from .models import Exam, StudentExamAttempt, ExamAnnouncement

@admin.action(description='Export Combined Results (CSV)')
def export_combined_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="combined_exam_results.csv"'
    writer = csv.writer(response)
    
    # Headers
    writer.writerow(['Exam Title', 'Shift (Start Time)', 'Student Username', 'Roll No', 'Score', 'Total Marks', 'Status', 'IP Address'])
    
    for exam in queryset:
        attempts = StudentExamAttempt.objects.filter(exam=exam, status='SUBMITTED')
        for attempt in attempts:
            roll_no = getattr(attempt.student, 'studentprofile', None)
            roll_str = roll_no.roll_number if roll_no else "N/A"
            
            writer.writerow([
                exam.title,
                exam.start_time.strftime("%Y-%m-%d %H:%M"),
                attempt.student.username,
                roll_str,
                attempt.score,
                exam.total_marks,
                attempt.status,
                attempt.ip_address
            ])
            
    return response

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'start_time', 'end_time', 'is_active', 'total_marks')
    list_filter = ('subject', 'is_active')
    filter_horizontal = ('questions',)
    save_as = True # Allows quick duplication for multiple shifts
    actions = [export_combined_csv]

@admin.register(StudentExamAttempt)
class StudentExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'status', 'score', 'start_time', 'ip_address')
    list_filter = ('status', 'exam')

@admin.register(ExamAnnouncement)
class ExamAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('message_preview', 'exam', 'recipient', 'created_at', 'is_active')
    list_filter = ('is_active', 'exam', 'recipient')
    search_fields = ('message', 'recipient__username')
    raw_id_fields = ('recipient',) # Better for selecting from many students
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
