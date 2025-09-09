from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('create/', views.create_student, name='create_student'),
    path('edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('delete/<int:pk>/', views.delete_student, name='delete_student'),
    path("<int:pk>/profile/", views.student_profile, name="student_profile"),
    path("upload/", views.upload_students, name="upload_students"),

    path("ajax/grade_update/", views.grade_update_ajax, name="grade_update_ajax"),
    path('ajax/attendance-update/', views.attendance_update_ajax, name='attendance_update_ajax'),

    path('report_card/<int:pk>/', views.student_report_card, name='student_report_card'),


    path('students/<int:pk>/download_qr/', views.download_student_qr, name='download_student_qr'),
]
