from django.db import models
from django.conf import settings
from students.models import StudentProfile
from classes.models import SchoolClass
from django.utils import timezone
from grades.models import ExamType

User = settings.AUTH_USER_MODEL

class Attendance(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LATE = 'late'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'حاضر'),
        (STATUS_ABSENT, 'غایب'),
        (STATUS_LATE, 'دیر'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendances')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    timestamp = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # اگر اسکن از طرف کاربر ثبت می‌کنیم

    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'school_class', 'date')
        ordering = ['-date', '-timestamp']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.school_class} - {self.date} - {self.status}"





class ExamAttendance(models.Model):
    """حاضری شاگرد در یک امتحان مشخص"""
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_SICK = 'sick'
    STATUS_LEAVE = 'leave'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'حاضر'),
        (STATUS_ABSENT, 'غایب'),
        (STATUS_SICK, 'مریض'),
        (STATUS_LEAVE, 'رخصت'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="exam_attendance")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="attendance")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="exam_attendance")

    present_days = models.PositiveIntegerField(default=0, verbose_name="روزهای حاضر")
    absent_days = models.PositiveIntegerField(default=0, verbose_name="روزهای غایب")
    sick_days = models.PositiveIntegerField(default=0, verbose_name="روزهای مریض")
    leave_days = models.PositiveIntegerField(default=0, verbose_name="روزهای رخصت")

    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="exam_attendance_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'exam_type', 'school_class')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam_type.name} (حاضر: {self.present_days}, غایب: {self.absent_days})"
