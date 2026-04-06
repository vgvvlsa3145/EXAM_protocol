from django.contrib import admin
from .models import Subject, Question, Option

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'subject', 'question_type', 'difficulty', 'marks')
    list_filter = ('subject', 'question_type', 'difficulty')
    inlines = [OptionInline]

admin.site.register(Subject)
