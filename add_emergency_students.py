import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\Sweet.Vellyn_Vgvvlsa\Desktop\VKR\exam')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import StudentProfile

User = get_user_model()

students_to_add = [
    {
        'roll_no': '23518-CM-022',
        'name': 'Manikanta',
        'password': 'Mani@123',
        'dept': 'DCME',
        'college': 'AGK',
        'year': 3
    },
    {
        'roll_no': '23518-CM-012',
        'name': 'Akash',
        'password': 'Akash@123',
        'dept': 'DCME',
        'college': 'AGK',
        'year': 3
    }
]

for s in students_to_add:
    user, created = User.objects.get_or_create(username=s['roll_no'])
    user.first_name = s['name']
    user.set_password(s['password'])
    user.role = 'STUDENT'
    user.save()
    
    profile, p_created = StudentProfile.objects.get_or_create(user=user)
    profile.roll_number = s['roll_no']
    profile.department = s['dept']
    profile.college_name = s['college']
    profile.year = s['year']
    profile.save()
    
    status = "Created" if created else "Updated"
    print(f"{status} student: {s['name']} ({s['roll_no']})")

print("Emergency student addition complete.")
