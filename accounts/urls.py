from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-detail/', views.student_detail_view, name='student_detail_view'), # Search handling
    path('student-detail/<int:student_id>/', views.student_detail_view, name='student_detail_view_id'),
    
    path('student-profile/', views.student_profile_view, name='student_profile'),
    
    # User Management
    path('manage-users/', views.manage_users, name='manage_users'),
    path('create-student/', views.create_student, name='create_student'),
    path('reset-password/<int:user_id>/', views.admin_password_reset, name='admin_password_reset'),
    path('api/search-students/', views.search_students_api, name='search_students_api'),
    path('admin-logout-user/<int:user_id>/', views.admin_logout_user, name='admin_logout_user'),
    path('admin-logout-all-students/', views.admin_logout_all_students, name='admin_logout_all_students'),
    
    # Login Approval
    path('waiting-approval/', views.waiting_approval, name='waiting_approval'),
    path('api/check-approval/', views.check_approval_api, name='check_approval_api'),
    
    # Passwordless Login Flow
    path('request-passwordless-login/', views.request_passwordless_login, name='request_passwordless_login'),
    path('check-passwordless-status/<int:request_id>/', views.check_passwordless_status, name='check_passwordless_status'),
    path('verify-passwordless-otp/', views.verify_passwordless_otp, name='verify_passwordless_otp'),
    path('login-with-token/<str:token>/', views.login_with_token, name='login_with_token'),
    
    # Admin Approval Management
    path('mgmt/pending-logins/', views.admin_list_login_requests, name='admin_list_login_requests'),
    path('mgmt/approve-request/<int:request_id>/', views.approve_login, name='admin_approve_request'),
    path('approve-login/<int:request_id>/', views.approve_login, name='approve_login'),
    path('reject-login/<int:request_id>/', views.reject_login, name='reject_login'),
]
