import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from exams.models import Exam
from questions.models import Subject, Question, Option
from accounts.models import User

try:
    subject, _ = Subject.objects.get_or_create(
        name='Test Subject', 
        defaults={'code': 'TEST101'}
    )
    
    e, created = Exam.objects.get_or_create(
        title='Auto Test Exam',
        defaults={
            'subject': subject,
            'duration_minutes': 60,
            'total_marks': 20,
            'is_active': True,
            'start_time': timezone.now() - timezone.timedelta(minutes=5),
            'end_time': timezone.now() + timezone.timedelta(days=1),
            'random_question_count': 0
        }
    )
    
    if created:
        print(f'Created Exam {e.id}: {e.title}')
        
        # Add a dummy question
        q1 = Question.objects.create(
            subject=subject,
            text="What is 2 + 2?",
            question_type='MCQ',
            marks=10,
            difficulty='EASY',
            category='Theory'
        )
        Option.objects.create(question=q1, text="3", is_correct=False)
        Option.objects.create(question=q1, text="4", is_correct=True)
        Option.objects.create(question=q1, text="5", is_correct=False)
        Option.objects.create(question=q1, text="6", is_correct=False)
        
        q2 = Question.objects.create(
            subject=subject,
            text="Which planet is known as the Red Planet?",
            question_type='MCQ',
            marks=10,
            difficulty='EASY',
            category='Theory'
        )
        Option.objects.create(question=q2, text="Earth", is_correct=False)
        Option.objects.create(question=q2, text="Jupiter", is_correct=False)
        Option.objects.create(question=q2, text="Mars", is_correct=True)
        Option.objects.create(question=q2, text="Venus", is_correct=False)
        
        e.questions.add(q1, q2)
        e.save()
        print("Added questions to the exam.")
    else:
        print(f'Exam {e.id} already exists.')
    
except Exception as ex:
    import traceback
    traceback.print_exc()
