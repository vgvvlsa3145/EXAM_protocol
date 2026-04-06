from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class Question(models.Model):
    TYPE_CHOICES = (
        ('MCQ', 'Multiple Choice'),
        ('DESCRIPTIVE', 'Descriptive'),
        ('CODE', 'Coding'),
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='MCQ')
    marks = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=20, choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')], default='MEDIUM')
    category = models.CharField(max_length=20, choices=[('Theory', 'Theory'), ('Program', 'Program')], default='Theory')
    explanation = models.TextField(null=True, blank=True, help_text="Reason for the correct answer")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.text[:50]}..."

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text
