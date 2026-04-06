from django.contrib import admin
from .models import StudentAnswer

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'marks_awarded')
    list_filter = ('attempt__exam',)
