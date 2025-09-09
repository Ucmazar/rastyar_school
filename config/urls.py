"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    return render(request, "accounts/home.html")


urlpatterns = [
    path('', home_view, name='home'),  # مسیر Home
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),  # مسیر شاگردان
    path('teachers/', include('teachers.urls')),  # مسیر »معلمین
    path("subjects/", include("subjects.urls")),
    path("classes/", include("classes.urls")),
    path('grades/', include('grades.urls')),  # ← اضافه شد
    path("attendance/", include("attendance.urls")),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)