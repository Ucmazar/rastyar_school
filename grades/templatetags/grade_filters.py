# grades/templatetags/grade_filters.py
from django import template
register = template.Library()

@register.filter
def get_grade(grades, subject):
    return grades.filter(subject=subject).first()
