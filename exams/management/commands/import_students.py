from django.core.management.base import BaseCommand
import csv
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Import students from CSV file'

    def handle(self, *args, **kwargs):
        file_path = 'students.csv'
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        count = 0
        updated = 0
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                roll_no = row['Roll No (PIN)'].strip()
                full_name = row['Student Name'].strip()
                department = row['Branch'].strip()
                college = row['College/Shift'].split('(')[0].strip()
                password = row['Password'].strip()
                
                # Split Name
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Check if user exists
                user, created = User.objects.get_or_create(username=roll_no)
                
                user.first_name = first_name
                user.last_name = last_name
                user.set_password(password)
                user.role = 'STUDENT'
                user.save()
                
                # Update/Create Profile
                profile, p_created = StudentProfile.objects.get_or_create(user=user)
                profile.roll_number = roll_no
                profile.department = department
                profile.college_name = college
                profile.year = 3  # Defaulted to 3rd Year as per requirement
                # User said "College/Shift -> Department or Year". Since Year is int, we used college_name. 
                # We'll leave year as default 1 or maybe we can infer it? 
                # Roll nos like 23518... suggest batch. But let's stick to default 1 for now.
                profile.save()
                
                if created:
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created: {roll_no} - {full_name}'))
                else:
                    updated += 1
                    self.stdout.write(self.style.WARNING(f'Updated: {roll_no} - {full_name}'))
                    
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} students. Updated {updated} existing.'))
