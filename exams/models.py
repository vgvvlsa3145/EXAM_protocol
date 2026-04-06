from django.db import models
from django.conf import settings
from questions.models import Question, Subject
from security.models import Lab

class Exam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    questions = models.ManyToManyField(Question, blank=True)
    random_question_count = models.PositiveIntegerField(null=True, blank=True, help_text="Total number of random questions. If set, logic below applies.")
    theory_count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of Theory questions to pick for this exam.")
    program_count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of Program questions to pick for this exam.")
    labs = models.ManyToManyField(Lab, blank=True, help_text="Restrict exam to specific labs")
    
    # Cheating Thresholds
    warning_threshold = models.PositiveIntegerField(default=3, help_text="Max violations before automatic submission")
    
    is_active = models.BooleanField(default=False)
    results_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.title

class StudentExamAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    submit_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)
    violation_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='IN_PROGRESS', choices=[('IN_PROGRESS', 'In Progress'), ('SUBMITTED', 'Submitted')])
    
    # Store IP used for attempt
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student} - {self.exam}"

class ExamAnnouncement(models.Model):
    message = models.TextField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True, help_text="If set, only effective for this exam. If empty, global.")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='received_announcements', help_text="If set, only this specific student will see the message.")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Announcement ({self.created_at.strftime('%H:%M')}): {self.message[:30]}..."
