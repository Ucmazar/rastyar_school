from django.db import models
from teachers.models import TeacherProfile
from students.models import StudentProfile
from subjects.models import SubjectGroup
from accounts.models import CustomUser

class SchoolClass(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="نام کلاس"
    )
    grade = models.CharField(
        max_length=50,
        verbose_name="درجه / سطح کلاس"
    )
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="classes",
        verbose_name="معلم کلاس"
    )
    students = models.ManyToManyField(
        StudentProfile,
        related_name="classes",
        blank=True,
        verbose_name="شاگردان"
    )
    subject_group = models.ForeignKey(
        SubjectGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes",
        verbose_name="گروه مضامین"
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_classes",
        verbose_name="ایجاد شده توسط"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "کلاس"
        verbose_name_plural = "کلاس‌ها"
        unique_together = ("name", "grade", "created_by")
        ordering = ['grade', 'name']  # مرتب‌سازی پیش‌فرض در ادمین

    def __str__(self):
        return f"{self.name} - {self.grade}"
