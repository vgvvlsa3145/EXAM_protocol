from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('exams/', include('exams.urls')),
    path('security/', include('security.urls')),
    path('faculty/', include('questions.urls')),
    path('results/', include('results.urls')),
    path('analytics/', include('analytics.urls')),
]
