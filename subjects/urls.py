from django.urls import path
from . import views

urlpatterns = [
    # گروه مضامین
    path("groups/", views.subjectgroup_list, name="subjectgroup_list"),
    path("groups/create/", views.subjectgroup_create, name="subjectgroup_create"),
    path("groups/update/<int:pk>/", views.subjectgroup_update, name="subjectgroup_update"),
    path("groups/delete/<int:pk>/", views.subjectgroup_delete, name="subjectgroup_delete"),
    
    # مضامین
    path("", views.subject_list, name="subject_list"),
    path("create/", views.subject_create, name="subject_create"),
    path("update/<int:pk>/", views.subject_update, name="subject_update"),
    path("delete/<int:pk>/", views.subject_delete, name="subject_delete"),
]
