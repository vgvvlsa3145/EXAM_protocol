from django.db import models
from exams.models import StudentExamAttempt
from questions.models import Question, Option

class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True, null=True) # For descriptive or code
    marks_awarded = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Ans: {self.question.id} by {self.attempt.student}"
