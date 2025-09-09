from django import forms
from accounts.models import CustomUser
from .models import TeacherProfile
from subjects.models import Subject
import random


class TeacherForm(forms.ModelForm):
    # فیلدهای کاربری
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="نام",
        error_messages={"required": "پر کردن این فیلد الزامی است."}
    )
    last_name = forms.CharField(max_length=30, required=False, label="نام خانوادگی")
    username = forms.CharField(max_length=150, required=False, label="نام کاربری")

    
    email = forms.EmailField(required=False, label="ایمیل")
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, label="رمز عبور")
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label="تکرار رمز عبور")

    class Meta:
        model = TeacherProfile
        fields = ["phone", "address", "date_of_birth", "subjects", "father_name"]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'subjects': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
        labels = {
            "phone": "شماره تماس",
            "father_name": "نام پدر",
            "address": "آدرس",
            "date_of_birth": "تاریخ تولد",
            "subjects": "مضمون",
        }

    def __init__(self, *args, **kwargs):
        self.instance_user = kwargs.pop('user_instance', None)
        creator = kwargs.pop('creator', None)  # کاربر جاری
        super().__init__(*args, **kwargs)

        # فقط مضامین ساخته‌شده توسط کاربر جاری
        if creator:
            self.fields['subjects'].queryset = Subject.objects.filter(created_by=creator)
        else:
            self.fields['subjects'].queryset = Subject.objects.none()

        # انتخاب‌های قبلی معلم را نگه دار
        if self.instance.pk:
            self.fields['subjects'].initial = self.instance.subjects.all()

        # پر کردن فیلدهای کاربری برای ویرایش
        if self.instance_user:
            self.fields['first_name'].initial = self.instance_user.first_name
            self.fields['last_name'].initial = self.instance_user.last_name
            self.fields['username'].initial = self.instance_user.username
            self.fields['email'].initial = self.instance_user.email
            self.fields['father_name'].initial = getattr(self.instance, 'father_name', '')

        self.creator = creator  # برای save ذخیره می‌کنیم

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")
        if pw1 or pw2:
            if pw1 != pw2:
                raise forms.ValidationError("رمزهای عبور یکسان نیستند")
        return cleaned_data

    def save(self, commit=True, instance=None):
        creator = self.creator

        if instance:  # حالت ویرایش
            teacher = instance
            user = teacher.user

            # بروزرسانی فیلدهای TeacherProfile
            teacher.father_name = self.cleaned_data.get("father_name", teacher.father_name)
            teacher.phone = self.cleaned_data.get("phone", teacher.phone)
            teacher.address = self.cleaned_data.get("address", teacher.address)
            teacher.date_of_birth = self.cleaned_data.get("date_of_birth", teacher.date_of_birth)

            if commit:
                teacher.save()
                if hasattr(self, 'save_m2m'):
                    self.save_m2m()  # ذخیره M2M فقط وقتی موجود باشد

            # بروزرسانی فیلدهای کاربری
            user.first_name = self.cleaned_data.get("first_name", user.first_name)
            user.last_name = self.cleaned_data.get("last_name", user.last_name)
            user.email = self.cleaned_data.get("email", user.email)
            password = self.cleaned_data.get("password1")
            if password:
                user.set_password(password)
            if commit:
                user.save()

            return teacher

        else:  # حالت ایجاد
            username = self.cleaned_data.get("username") or f"teacher{random.randint(1, 9999)*10}"
            password = self.cleaned_data.get("password1") or "Rastyar123"

            # ایجاد کاربر جدید
            user = CustomUser.objects.create_user(
                username=username,
                email=self.cleaned_data.get("email", ""),
                password=password,
                first_name=self.cleaned_data.get("first_name"),
                last_name=self.cleaned_data.get("last_name"),
                role="teacher"
            )

            # ایجاد پروفایل Teacher
            teacher = super().save(commit=False)
            teacher.user = user
            teacher.father_name = self.cleaned_data.get("father_name", "")
            teacher.phone = self.cleaned_data.get("phone", "")
            teacher.address = self.cleaned_data.get("address", "")
            teacher.date_of_birth = self.cleaned_data.get("date_of_birth", None)
            if creator:
                teacher.created_by = creator

            if commit:
                teacher.save()
                if hasattr(self, 'save_m2m'):
                    self.save_m2m()  # ذخیره M2M

            return teacher





class TeacherProfileForm(forms.ModelForm):
    # فیلدهای کاربری
    first_name = forms.CharField(required=True, label="نام")
    last_name = forms.CharField(required=False, label="نام خانوادگی")
    email = forms.EmailField(required=False, label="ایمیل")

    class Meta:
        model = TeacherProfile
        fields = ["father_name", "address", "date_of_birth", "subjects", "phone"]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'subjects': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
        labels = {

            "phone": "شماره تماس",
            "father_name": "نام پدر",
            "address": "آدرس",
            "date_of_birth": "تاریخ تولد",
            "subjects": "مضمون",
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)

        # فیلتر مضامین
        if creator:
            self.fields['subjects'].queryset = Subject.objects.filter(created_by=creator)
        else:
            self.fields['subjects'].queryset = Subject.objects.all()

        # انتخاب‌های قبلی
        if self.instance.pk:
            self.fields['subjects'].initial = self.instance.subjects.all()

        # پر کردن فیلدهای کاربری
        if self.user_instance:
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['email'].initial = self.user_instance.email

    def save(self, commit=True):
        teacher = super().save(commit=False)

        # ذخیره اطلاعات پروفایل
        if commit:
            teacher.save()
            self.save_m2m()

        # ذخیره اطلاعات کاربر
        if self.user_instance:
            self.user_instance.first_name = self.cleaned_data['first_name']
            self.user_instance.last_name = self.cleaned_data['last_name']
            self.user_instance.email = self.cleaned_data['email']
            if commit:
                self.user_instance.save()

        return teacher
