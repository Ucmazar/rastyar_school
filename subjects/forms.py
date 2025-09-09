# subjects/forms.py
from django import forms
from .models import Subject, SubjectGroup
from django.contrib.auth import get_user_model


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام مضمون'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop("creator", None)  # کاربر جاری
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        # بررسی تکراری بودن فقط برای همین کاربر
        if self.creator:
            qs = Subject.objects.filter(name__iexact=name, created_by=self.creator)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)  # در حالت ویرایش خودش رو نادیده بگیره
            if qs.exists():
                raise forms.ValidationError("این مضمون قبلاً توسط شما ثبت شده است.")
        return name

    def save(self, commit=True):
        subject = super().save(commit=False)
        if not subject.pk and self.creator:  # فقط در حالت ایجاد
            subject.created_by = self.creator
        if commit:
            subject.save()
        return subject



User = get_user_model()

class SubjectGroupForm(forms.ModelForm):
    class Meta:
        model = SubjectGroup
        fields = ['name', 'subjects', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام گروه'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات'
            }),
            'subjects': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            # مضامینی که کاربر فعلی ساخته
            user_subjects = Subject.objects.filter(created_by=user)

            # اگر کاربر معلم بود → مضامین سوپرادمین‌ها هم اضافه شود
            if hasattr(user, "teacherprofile"):
                super_admins = User.objects.filter(is_superuser=True)
                admin_subjects = Subject.objects.filter(created_by__in=super_admins)
                queryset = (user_subjects | admin_subjects).distinct()
            else:
                queryset = user_subjects

            self.fields['subjects'].queryset = queryset
