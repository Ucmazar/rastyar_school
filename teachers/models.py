from django.db import models
from accounts.models import BaseProfile
from django.conf import settings
from subjects.models import Subject

User = settings.AUTH_USER_MODEL

class TeacherProfile(BaseProfile):
    subjects = models.ManyToManyField("subjects.Subject", related_name="teachers")  
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers_created',
        limit_choices_to={'role__in': ['admin']}
    )

    def __str__(self):
        # می‌توان first_name و last_name را نمایش داد
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

