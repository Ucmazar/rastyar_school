from django import forms
from .models import Grade, ExamType
from django.db.models import Q

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'school_class', 'exam_type', 'score']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'school_class': forms.Select(attrs={'class': 'form-control'}),
            'exam_type': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }



class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ['name', 'description', 'academic_year', 'academic_year_days']  # اضافه شدن سال و روزهای آموزشی
        labels = {
            'name': 'نام امتحان',
            'description': 'توضیحات امتحان',
            'academic_year': 'سال تحصیلی',
            'academic_year_days': 'تعداد روزهای آموزشی'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: امتحان نوبت اول'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'توضیحات امتحان',
                'rows': 3
            }),
            'academic_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 1404'
            }),
            'academic_year_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 200'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # کاربر جاری
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance
