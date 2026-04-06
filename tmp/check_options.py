import sys
import os
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import models
from exams.models import Exam
from questions.models import Option

# 1. Find the exam
exam = Exam.objects.filter(title__icontains='JAVA').first()
if not exam:
    print("Exam not found!")
    sys.exit(1)

print(f"Checking Exam: {exam.title} (ID: {exam.id})")

# 2. Find options
# We search for the phrase anywhere first to see the variations
opts = Option.objects.filter(question__exam=exam).filter(
    models.Q(text__icontains="standard")
)

print(f"Found {opts.count()} options containing 'standard'.")

patterns = [
    " (standard implementation)",
    "(standard implementation)",
    " standard implementation",
    " (standard implenataion)",
    "(standard implenataion)",
    " standard implenataion",
    "standard implementation",
    "standard implenataion"
]

import json

results = []
for o in opts:
    original_text = o.text
    new_text = original_text
    
    found_pattern = None
    for p in patterns:
        if original_text.lower().strip().endswith(p.lower()):
            idx = original_text.lower().rfind(p.lower())
            new_text = original_text[:idx].strip()
            found_pattern = p
            break
            
    if new_text != original_text:
        results.append({
            'id': o.id,
            'old': original_text,
            'new': new_text,
            'pattern': found_pattern
        })
        # PERFORM ACTUAL UPDATE
        o.text = new_text
        o.save()

output_path = os.path.join(os.getcwd(), 'tmp', 'cleanup_report.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Cleanup complete. Updated {len(results)} options. Report written to {output_path}")
