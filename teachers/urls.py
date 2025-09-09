from django.urls import path
from . import views

urlpatterns = [
    path("", views.teacher_list, name="teacher_list"),
    path("create/", views.create_teacher, name="create_teacher"),
    path("<int:pk>/edit/", views.edit_teacher, name="edit_teacher"),  # ویرایش معلم
    path("<int:pk>/delete/", views.delete_teacher, name="delete_teacher"),  # حذف معلم
    path("profile/edit/", views.teacher_profile_edit, name="teacher_profile_edit"),
    path("profile/<int:pk>/", views.teacher_profile, name="teacher_profile"),
]
