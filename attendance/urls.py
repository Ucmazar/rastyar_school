from django.urls import path
from . import views

urlpatterns = [
    path("mark/", views.mark_attendance, name="mark_attendance"),  # فرم ساده (اختیاری)
    path("scan/", views.scan_attendance_page, name="scan_attendance_page"),  # صفحه HTML با اسکنر
    path("mark-qr/", views.mark_attendance_qr, name="mark_attendance_qr"),  # ویو POST واقعی
    path("latest/", views.latest_attendance, name="latest_attendance"),


    path('exam_attendance/<int:student_id>/<int:exam_id>/', views.exam_attendance_edit, name='exam_attendance_edit'),
    
]
