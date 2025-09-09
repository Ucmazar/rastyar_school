from django import forms
from .models import ExamAttendance

class ExamAttendanceForm(forms.ModelForm):
    class Meta:
        model = ExamAttendance
        fields = ['present_days', 'absent_days', 'sick_days', 'leave_days']
        widgets = {
            'present_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'absent_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'sick_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'leave_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        """
        اگر instance پاس داده شود، فرم برای آپدیت مقدارهای موجود را پر می‌کند.
        """
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['present_days'].initial = getattr(self.instance, 'present_days', 0)
            self.fields['absent_days'].initial = getattr(self.instance, 'absent_days', 0)
            self.fields['sick_days'].initial = getattr(self.instance, 'sick_days', 0)
            self.fields['leave_days'].initial = getattr(self.instance, 'leave_days', 0)
