from django.db import models
from students.models import StudentProfile
from classes.models import SchoolClass
from subjects.models import Subject
from accounts.models import CustomUser
from django.conf import settings

User = CustomUser


class ExamType(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام امتحان")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    academic_year  = models.PositiveIntegerField( blank=True, null=True)   # 1403, 1404 ...
    academic_year_days  = models.PositiveIntegerField(blank=True, null=True)          # تعداد روزهای آموزشی
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ایجاد شده توسط"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.total_days}"


    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ایجاد شده توسط"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.academic_year.year}"



class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="grades")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="grades", null=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="grades")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="grades", null=True, blank=True)  # ← اضافه شد
    score = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="grades_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'school_class', 'exam_type')  # یکتا برای هر شاگرد و مضمون و کلاس

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.score}"


