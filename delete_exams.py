import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from exams.models import Exam

exams_to_delete = [
    "Live System Check Exam",
    "Final Semester Demo Exam"
]

for title in exams_to_delete:
    exams = Exam.objects.filter(title__icontains=title)
    if exams.exists():
        print(f"Deleting {exams.count()} exams matching '{title}'")
        exams.delete()
    else:
        print(f"No exams found matching '{title}'")

print("Done deleting exams.")
