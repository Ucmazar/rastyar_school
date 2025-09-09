from django import forms
from accounts.models import CustomUser
from .models import StudentProfile
import random

class StudentCreationForm(forms.ModelForm):
    # فیلدهای کاربری با لیبل فارسی و پیام خطا
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="نام",
        error_messages={"required": "پر کردن این فیلد الزامی است."}
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label="نام خانوادگی"
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        label="نام کاربری",
        help_text="این فیلد هنگام ویرایش تغییر نمی‌کند."
    )
    email = forms.EmailField(
        required=False,
        label="ایمیل",
        error_messages={"invalid": "لطفاً یک ایمیل معتبر وارد کنید."}
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        initial="Rastyar123",
        required=False,
        label="رمز عبور"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        initial="Rastyar123",
        required=False,
        label="تکرار رمز عبور"
    )

    # فیلدهای StudentProfile با پیام خطای فارسی
    phone = forms.CharField(max_length=20, required=False, label="تلفن")
    father_name = forms.CharField(
        max_length=100,
        required=True,
        label="نام پدر",
        error_messages={"required": "پر کردن این فیلد الزامی است."}
    )
    grandfather_name = forms.CharField(
        max_length=100,
        required=True,
        label="نام پدرکلان",
        error_messages={"required": "پر کردن این فیلد الزامی است."}
    )
    student_number = forms.CharField(
        max_length=100,
        required=True,
        label="نمبر اساس",
        error_messages={"required": "پر کردن این فیلد الزامی است."}
    )
    address = forms.CharField(widget=forms.Textarea, required=False, label="آدرس")
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="تاریخ تولد",
        error_messages={"invalid": "لطفاً یک تاریخ معتبر وارد کنید."}
    )

    class Meta:
        model = StudentProfile
        fields = [
            'phone', 'address', 'date_of_birth',
            'father_name', 'grandfather_name', 'student_number'
        ]

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("رمزهای عبور یکسان نیستند")
        return cleaned_data

    def save(self, commit=True, creator=None, instance=None):
        """
        اگر instance داده شود، فقط StudentProfile و فیلدهای قابل تغییر آپدیت می‌شوند.
        اگر instance داده نشود، یک کاربر جدید ساخته می‌شود.
        """
        if instance:  # حالت ویرایش
            student = instance
            user = student.user

            # آپدیت فقط فیلدهای قابل تغییر
            student.father_name = self.cleaned_data.get("father_name", student.father_name)
            student.grandfather_name = self.cleaned_data.get("grandfather_name", student.grandfather_name)
            student.student_number = self.cleaned_data.get("student_number", student.student_number)
            student.phone = self.cleaned_data.get("phone", student.phone)
            student.address = self.cleaned_data.get("address", student.address)
            student.date_of_birth = self.cleaned_data.get("date_of_birth", student.date_of_birth)

            # آپدیت نام و نام خانوادگی کاربر بدون تغییر username و created_by
            user.first_name = self.cleaned_data.get("first_name", user.first_name)
            user.last_name = self.cleaned_data.get("last_name", user.last_name)
            user.email = self.cleaned_data.get("email", user.email)

            if commit:
                user.save()
                student.save()
            return student

        else:  # حالت ایجاد
            username = self.cleaned_data.get("username")
            if not username:
                username = f"rastyar{random.randint(1, 9999)*10}"

            password = self.cleaned_data.get("password1") or "Rastyar123"

            user = CustomUser.objects.create_user(
                username=username,
                email=self.cleaned_data.get("email", ""),
                password=password,
                first_name=self.cleaned_data.get("first_name"),
                last_name=self.cleaned_data.get("last_name"),
                role="student"
            )

            student = super().save(commit=False)
            student.user = user
            student.father_name = self.cleaned_data.get("father_name", "")
            student.grandfather_name = self.cleaned_data.get("grandfather_name", "")
            student.student_number = self.cleaned_data.get("student_number", "")
            student.phone = self.cleaned_data.get("phone")
            student.address = self.cleaned_data.get("address")
            student.date_of_birth = self.cleaned_data.get("date_of_birth", "")
            
            if commit:
                student.save()
            return student

from django import forms

class StudentExcelUploadForm(forms.Form):
    file = forms.FileField(label="فایل اکسل شاگردان")
