# attendance/templatetags/attendance_tags.py
from django import template

register = template.Library()

@register.filter
def get_grade(student, args):
    subject, exam_type = args.split(',')
    return student.grades.filter(subject__id=subject, exam_type__id=exam_type).first()


@register.filter
def get_attendance(attendance_dict, student_id):
    return attendance_dict.get(student_id)

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, 0)
