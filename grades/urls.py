from django.urls import path
from . import views

urlpatterns = [
    path('entry/', views.grade_entry, name='grade_entry'),
    path('export/', views.export_students_grades, name='export_students_grades'),  # ← خروجی CSV
    path('ajax/update/', views.grade_update_ajax, name='grade_update_ajax'),

    path('exams/', views.examtype_list, name='examtype_list'),
    path('exams/create/', views.examtype_create, name='examtype_create'),
    path('exams/<int:pk>/edit/', views.examtype_update, name='examtype_update'),
    path('exams/<int:pk>/delete/', views.examtype_delete, name='examtype_delete'),

    path('ajax/load-exam-types/', views.load_exam_types, name='ajax_load_exam_types'),



]
