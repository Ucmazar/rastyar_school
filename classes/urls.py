from django.urls import path
from . import views

urlpatterns = [
    path("", views.class_list, name="class_list"),
    path("create/", views.create_class, name="create_class"),
    path("<int:pk>/edit/", views.update_class, name="update_class"),
    path("update/<int:pk>/", views.update_class, name="update_class"),  # ویرایش کلاس
    path("delete/<int:pk>/", views.delete_class, name="delete_class"),  # حذف کلاس

    path("class_print_zawabet/<int:pk>/", views.class_print_zawabet, name="class_print_zawabet"),
    path("class_print_shoqa/<int:pk>/", views.class_print_shoqa, name="class_print_shoqa"),
    path('export_shoqa/<int:pk>/', views.export_class_shoqaA4, name='export_class_shoqaA4'),
    path('export_zawabet/<int:pk>/', views.export_class_zawabetA4, name='export_class_zawabetA4'),
    path('grade_attendance/<int:pk>/', views.load_grade_attendance, name='load_grade_attendance'),

    path("<int:pk>/report_cards/", views.class_report_cards, name="class_report_cards"),
    path('<int:class_id>/download_qr/', views.download_class_qr, name='download_class_qr'),

    path('grades/entry/', views.grade_entry, name='grade_entry'),


]
