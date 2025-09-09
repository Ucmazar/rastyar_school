from django import forms
from .models import SchoolClass
from students.models import StudentProfile
from teachers.models import TeacherProfile
from subjects.models import SubjectGroup
from django.contrib.auth import get_user_model

User = get_user_model()

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "grade", "teacher", "students", "subject_group"]
        widgets = {
            'students': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'teacher': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'subject_group': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
        labels = {
            "name": "نام کلاس",
            "grade": "درجه / سطح کلاس",
            "teacher": "معلم کلاس",
            "students": "شاگردان",
            "subject_group": "گروه مضامین",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.user = user  # 👈 اضافه شد

        # ---------- پیام خطا ----------
        self.fields['name'].error_messages = {'required': 'وارد کردن نام کلاس الزامی است.'}
        self.fields['grade'].error_messages = {'required': 'وارد کردن درجه کلاس الزامی است.'}
        self.fields['teacher'].error_messages = {'required': 'انتخاب معلم الزامی است.'}
        self.fields['subject_group'].error_messages = {'required': 'انتخاب گروه مضامین الزامی است.'}
        self.fields['students'].error_messages = {'required': 'حداقل یک شاگرد انتخاب شود.'}

        # ---------- معلم ----------
        if user and user.role == "teacher":
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
                self.fields['teacher'].queryset = TeacherProfile.objects.filter(pk=teacher_profile.pk)
                self.fields['teacher'].initial = teacher_profile
                self.fields['teacher'].disabled = True
            except TeacherProfile.DoesNotExist:
                self.fields['teacher'].queryset = TeacherProfile.objects.none()
                self.fields['teacher'].disabled = True

        elif user and user.role == "admin":
            self.fields['teacher'].queryset = TeacherProfile.objects.filter(created_by=user)
            self.fields['teacher'].disabled = False
        else:
            self.fields['teacher'].queryset = TeacherProfile.objects.none()
            self.fields['teacher'].disabled = True

        # ---------- شاگردان ----------
        if self.instance and self.instance.pk:
            # شاگردان این کلاس + شاگردان آزاد ایجادشده توسط کاربر جاری
            self.fields['students'].queryset = (
                StudentProfile.objects.filter(classes__isnull=True, created_by=user) | self.instance.students.all()
            ).distinct()
        else:
            # فقط شاگردان آزاد ایجاد شده توسط کاربر جاری
            self.fields['students'].queryset = StudentProfile.objects.filter(classes__isnull=True, created_by=user)

        # ---------- گروه مضامین ----------
        if user:
            if user.role == "teacher":
                super_admins = User.objects.filter(is_superuser=True)
                self.fields['subject_group'].queryset = SubjectGroup.objects.filter(
                    created_by__in=list(super_admins) + [user]
                )
            elif user.role == "admin":
                self.fields['subject_group'].queryset = SubjectGroup.objects.filter(created_by=user)
            else:
                self.fields['subject_group'].queryset = SubjectGroup.objects.none()
        else:
            self.fields['subject_group'].queryset = SubjectGroup.objects.none()

        # ---------- نمایش خوانا ----------
        self.fields['students'].label_from_instance = lambda obj: f"{obj.user.full_name_display} - فرزند: {obj.father_name}"
        self.fields['teacher'].label_from_instance = lambda obj: obj.user.full_name_display

    def save(self, commit=True):
        instance = super().save(commit=False)
        # اگر کاربر معلم است، مطمئن شو که teacher ست شده
        if self.user and self.user.role == "teacher":
            teacher_profile = TeacherProfile.objects.get(user=self.user)
            instance.teacher = teacher_profile
        if commit:
            instance.save()
            self.save_m2m()
        return instance
