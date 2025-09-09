from django.db import models
from django.conf import settings
from accounts.models import BaseProfile
from subjects.models import Subject
import uuid

User = settings.AUTH_USER_MODEL

class StudentProfile(BaseProfile):
    
    grandfather_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام پدر", )
    
    student_number = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="نمبر اساس")


    attendance_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='qrcodes/students', blank=True, null=True)
    

    # چه کسی شاگرد را ثبت کرده است (مدیر یا معلم)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students_created",
        limit_choices_to={'role__in': ['teacher', 'admin']}
    )

    def __str__(self):
        # استفاده از نام و تخلص از BaseProfile
        if hasattr(self, 'first_name') and hasattr(self, 'last_name'):
            return f"{self.first_name} {self.last_name}"
        elif hasattr(self.user, 'first_name') and hasattr(self.user, 'last_name'):
            # اگر BaseProfile فیلدها را ندارد، از user بگیریم
            return f"{self.user.first_name} {self.user.last_name}"
        else:
            # fallback به username
            return str(self.user)


            