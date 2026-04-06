import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, LoginRequest

def run_test():
    # Setup test user
    student, created = User.objects.get_or_create(username='test_student', role='STUDENT')
    if created:
        student.set_password('password123')
        student.save()
        
    admin, created = User.objects.get_or_create(username='admin_boss', role='ADMIN')
    if created:
        admin.set_password('password123')
        admin.save()
        
    # Clear previous requests
    LoginRequest.objects.all().delete()
    
    print("--- Testing Login Flow ---")
    c = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0')
    
    # 1. Login as student
    response = c.post('/login/', {'username': 'test_student', 'password': 'password123'})
    print(f"Login Redirect Status: {response.status_code}")
    print(f"Redirect URL: {response.url}")
    
    if response.url == '/waiting-approval/':
        print("[SUCCESS] Student redirected to waiting page.")
    else:
        print("[FAIL] Student was not redirected to waiting page!")
        
    # 2. Check Database for LoginRequest with device tracking
    req = LoginRequest.objects.first()
    if req:
        print(f"\n[SUCCESS] LoginRequest created!")
        print(f" - Student: {req.user.username}")
        print(f" - IP: {req.ip_address}")
        print(f" - MAC: {req.mac_address}")
        print(f" - Platform: {req.platform}")
        print(f" - Device/Browser: {req.device_info}")
        print(f" - User Agent: {req.user_agent}")
        print(f" - Status: {req.status}")
    else:
        print("\n[FAIL] No LoginRequest found in database!")
        return

    # 3. Simulate Admin Approval
    print("\n--- Simulating Admin Approval ---")
    c_admin = Client()
    c_admin.post('/login/', {'username': 'admin_boss', 'password': 'password123'})
    
    # Approve the request
    approve_response = c_admin.get(f'/approve-login/{req.id}/')
    print(f"Admin Approval Redirect Status: {approve_response.status_code}")
    
    # Check DB again
    req.refresh_from_db()
    print(f"Updated request status: {req.status}")
    
    if req.status == 'APPROVED':
        print("[SUCCESS] Admin successfully approved the login.")
    else:
        print("[FAIL] Admin approval failed.")
        
    # 4. Check if student can now access dashboard
    dashboard_response = c.get('/dashboard/')
    if dashboard_response.status_code == 302 and dashboard_response.url == '/exams/dashboard/':
         # actually, the redirect might be to 'student_dashboard'
         print(f"[NOTE] Dashboard redirect after approval: {dashboard_response.url}")
    elif dashboard_response.status_code == 302 and '/waiting-approval/' in dashboard_response.url:
         print("[FAIL] Student is still blocked after approval!")
    else:
         print(f"Student dashboard access status: {dashboard_response.status_code}, URL: {getattr(dashboard_response, 'url', 'N/A')}")
         print("[SUCCESS] Student bypassed the waiting page.")

if __name__ == '__main__':
    run_test()
