from django.db import models
from django.utils import timezone
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام مضمون")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ ایجاد")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subjects",
        verbose_name="ایجاد شده توسط",
        null=True,
    )

    def __str__(self):
        return self.name


class SubjectGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام گروه")
    subjects = models.ManyToManyField(
        Subject,  # مستقیم به مدل وصل میشه (نیازی به "Subject" رشته‌ای نیست)
        related_name="groups",
        verbose_name="مضامین",
    )
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ ایجاد")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subject_groups",
        verbose_name="ایجاد شده توسط",
    )

    def __str__(self):
        return self.name
