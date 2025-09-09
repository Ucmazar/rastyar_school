from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# نقش‌ها برای کاربر
class UserRole(models.TextChoices):
    ADMIN = "admin", "مدیر مکتب"
    TEACHER = "teacher", "معلم"
    STUDENT = "student", "شاگرد"
    PARENT = "parent", "والدین"


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.TEACHER
    )
    created_at = models.DateTimeField(default=timezone.now)  # اضافه کنید
    

    
    @property
    def full_name_display(self):
        # ترکیب first_name و last_name
        full_name = f"{self.first_name} {self.last_name}".strip()
        # اگر خالی بود، username نمایش داده شود
        return full_name if full_name else self.username

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# پروفایل پایه (برای همه نقش‌ها)
class BaseProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    class Meta:
        abstract = True  # این مدل مستقیم ساخته نمیشه، فقط پایه است

    def __str__(self):
        # نمایش نام کامل از CustomUser
        return self.user.full_name_display