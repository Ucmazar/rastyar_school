# Python built-in
import csv

# Django
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

# Local apps
from accounts.permissions import role_required, owner_or_admin
from .models import Grade, ExamType
from .forms import ExamTypeForm
from classes.models import SchoolClass
from students.models import StudentProfile
from subjects.models import Subject
from attendance.models import ExamAttendance, Attendance


# ----------------------------------
# AJAX ثبت یا بروزرسانی نمره با exam_type
# ----------------------------------
@login_required
@csrf_exempt
@role_required(['admin', 'teacher'])
def grade_update_ajax(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        student_id = request.POST.get("student_id")
        class_id = request.POST.get("class_id")
        subject_id = request.POST.get('subject_id')
        score = request.POST.get("score")
        present = request.POST.get("present")
        absent = request.POST.get("absent")
        sick = request.POST.get("sick")
        leave = request.POST.get("leave")

        try:
            student_id = request.POST.get('student_id')
            subject_id = request.POST.get('subject_id')
            class_id = request.POST.get('class_id')
            exam_id = request.POST.get('exam_type_id')
            score = request.POST.get('score', '0')
            present = request.POST.get('present', 0)
            absent = request.POST.get('absent', 0)
            sick = request.POST.get('sick', 0)
            leave = request.POST.get('leave', 0)

            student = StudentProfile.objects.get(id=student_id)
            school_class = SchoolClass.objects.get(id=class_id)
            subject = Subject.objects.get(id=subject_id)
            exam_type = ExamType.objects.get(id=exam_id)

            # ثبت یا بروزرسانی نمره
            score = request.POST.get('score', 0)  # پیش‌فرض صفر
            try:
                score_float = float(score)
                Grade.objects.update_or_create(
                    student=student,
                    school_class=school_class,
                    subject=subject,
                    exam_type=exam_type,
                    defaults={'score': score_float}
                )
            except ValueError:
                score_float = 0

            # ثبت یا بروزرسانی حضور و غیاب
            ExamAttendance.objects.update_or_create(
                student=student,
                school_class=school_class,
                exam_type=exam_type,
                defaults={
                    'present_days': int(present) if present else 0,
                    'absent_days': int(absent) if absent else 0,
                    'sick_days': int(sick) if sick else 0,
                    'leave_days': int(leave) if leave else 0,
                    'recorded_by': request.user
                }
            )


            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})


# ----------------------------------
# فرم ثبت نمره
# ----------------------------------


User = get_user_model()
@login_required
@role_required(['admin', 'teacher'])
def grade_entry(request):
    # کلاس‌هایی که کاربر جاری ساخته
    classes = SchoolClass.objects.filter(created_by=request.user)
    selected_class_id = request.GET.get('class')
    selected_exam_id = request.GET.get('exam_type')

    selected_class = None
    selected_exam_type = None
    students = []
    subjects = []

    # مقدار پیش‌فرض برای attendance_data
    attendance_data = {}

    # امتحانات کاربر جاری (و اگر معلم است + سوپرادمین‌ها)
    user_exams = ExamType.objects.filter(created_by=request.user)
    if hasattr(request.user, "teacherprofile"):
        super_admins = User.objects.filter(is_superuser=True)
        admin_exams = ExamType.objects.filter(created_by__in=super_admins)
        exam_types = (user_exams | admin_exams).distinct()
    else:
        exam_types = user_exams

    # اگر کلاس انتخاب شد
    if selected_class_id:
        try:
            selected_class = SchoolClass.objects.get(id=selected_class_id, created_by=request.user)
            # فقط شاگردانی که داخل کلاس هستند و توسط کاربر جاری ثبت شده‌اند
            students = selected_class.students.filter(created_by=request.user)


            # گرفتن مضامین
            if selected_class.subject_group:
                subjects = selected_class.subject_group.subjects.all()
            else:
                subjects = []

            # اگر امتحان انتخاب شد
            if selected_exam_id:
                try:
                    selected_exam_type = exam_types.get(id=selected_exam_id)
                except ExamType.DoesNotExist:
                    selected_exam_type = None

            # ذخیره نمرات و حاضری
            if request.method == "POST" and selected_exam_type:
                for student in students:
                    # ذخیره نمرات
                    for subject in subjects:
                        key = f"score_{student.id}_{subject.id}"
                        score = request.POST.get(key)
                        if score:
                            Grade.objects.update_or_create(
                                student=student,
                                subject=subject,
                                school_class=selected_class,
                                exam_type=selected_exam_type,
                                defaults={'score': score, 'created_by': request.user}
                            )

                    # ذخیره حاضری
                    present = request.POST.get(f'present_{student.id}', 0) or 0
                    absent = request.POST.get(f'absent_{student.id}', 0) or 0
                    sick = request.POST.get(f'sick_{student.id}', 0) or 0
                    leave = request.POST.get(f'leave_{student.id}', 0) or 0

                    ExamAttendance.objects.update_or_create(
                        student=student,
                        school_class=selected_class,
                        exam_type=selected_exam_type,
                        defaults={
                            'present_days': present,
                            'absent_days': absent,
                            'sick_days': sick,
                            'leave_days': leave,
                            'recorded_by': request.user
                        }
                    )

                return redirect(f"{request.path}?class={selected_class.id}&exam_type={selected_exam_type.id}")

            # گرفتن داده‌های موجود برای نمایش
            attendance_qs = ExamAttendance.objects.filter(
                school_class=selected_class,
                exam_type=selected_exam_type
            ) if selected_exam_type else ExamAttendance.objects.none()

            attendance_data = {att.student.id: att for att in attendance_qs}

        except SchoolClass.DoesNotExist:
            selected_class = None
            students = []
            subjects = []

    context = {
        "classes": classes,
        "selected_class": selected_class,
        "students": students,
        "subjects": subjects,
        "exam_types": exam_types,
        "selected_exam_type": selected_exam_type,
        "attendance_data": attendance_data,
    }

    return render(request, "grades/grade/grade_entry.html", context)

# ----------------------------------
# خروجی اکسل نمرات
# ----------------------------------
@login_required
def export_students_grades(request):
    # دریافت کلاس و امتحان انتخابی از پارامترهای GET
    selected_class_id = request.GET.get('class')
    selected_exam_id = request.GET.get('exam_type')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_grades.csv"'
    response.write('\ufeff'.encode('utf-8'))  # BOM برای Excel

    writer = csv.writer(response)

    # بررسی کلاس انتخابی
    if selected_class_id:
        try:
            selected_class = SchoolClass.objects.get(id=selected_class_id, created_by=request.user)
            students = selected_class.students.all()
        except SchoolClass.DoesNotExist:
            students = []
            selected_class = None
    else:
        students = []
        selected_class = None

    # بررسی امتحان انتخابی
    selected_exam_type = None
    if selected_exam_id:
        try:
            selected_exam_type = ExamType.objects.get(id=selected_exam_id)
        except ExamType.DoesNotExist:
            selected_exam_type = None

    # گرفتن همه مضامین مرتبط با کلاس
    subjects = Subject.objects.filter(grades__school_class=selected_class).distinct() if selected_class else []

    # نوشتن هدر
    header = ["نام کامل", "نام پدر", "نام پدر کلان", "شماره تذکره", "نمبر اساس", "صنف"]
    for subject in subjects:
        header.append(subject.name)
    writer.writerow(header)

    # نوشتن داده‌ها
    for student in students:
        row = [
            f"{student.user.first_name} {student.user.last_name}",  # نام کامل
            student.father_name if hasattr(student, 'father_name') else "",  # نام پدر
            student.grandfather_name if hasattr(student, 'grandfather_name') else "",  # نام پدر کلان
            student.id_number if hasattr(student, 'id_number') else "",  # شماره تذکره
            student.student_number if hasattr(student, 'student_number') else "",  # شماره اساس
            selected_class.name if selected_class else ""  # صنف
        ]

        for subject in subjects:
            grade_obj = Grade.objects.filter(
                student=student,
                subject=subject,
                school_class=selected_class,
                exam_type=selected_exam_type
            ).first()
            row.append(grade_obj.score if grade_obj else "")
        writer.writerow(row)

    return response

# ----------------------------------
# CRUD ExamType
# ----------------------------------
User = get_user_model()

@login_required
def examtype_list(request):
    user = request.user

    # امتحانات ساخته شده توسط کاربر فعلی
    user_exams = ExamType.objects.filter(created_by=user)

    # اگر معلم است → امتحانات ساخته شده توسط سوپرادمین‌ها را هم اضافه کن
    if hasattr(user, "teacherprofile"):
        super_admins = User.objects.filter(is_superuser=True)
        admin_exams = ExamType.objects.filter(created_by__in=super_admins)
        exams = (user_exams | admin_exams).distinct()
    else:
        exams = user_exams

    return render(request, "grades/examtype/examtype_list.html", {"exams": exams})



@login_required
@role_required(['admin', 'teacher'])
def examtype_create(request):
    if request.method == 'POST':
        form = ExamTypeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()  # دیگر خطایی ندارد
            return redirect('examtype_list')
    else:
        form = ExamTypeForm(user=request.user)

    return render(request, 'grades/examtype/examtype_form.html', {'form': form})




@login_required
@owner_or_admin(owner_attr="user")
def examtype_update(request, pk):
    exam = get_object_or_404(ExamType, pk=pk)
    if request.method == 'POST':
        form = ExamTypeForm(request.POST, instance=exam, user=request.user)  # اضافه شد
        if form.is_valid():
            form.save()
            return redirect('examtype_list')
    else:
        form = ExamTypeForm(instance=exam, user=request.user)  # اضافه شد

    return render(request, 'grades/examtype/examtype_form.html', {'form': form})



@login_required
@owner_or_admin(owner_attr="user")
def examtype_delete(request, pk):
    exam = get_object_or_404(ExamType, pk=pk)
    if request.method == 'POST':
        exam.delete()
        return redirect('examtype_list')
    return render(request, 'grades/examtype/examtype_confirm_delete.html', {'exam': exam})


# ----------------------------------
# AJAX برای بارگذاری امتحانات بر اساس کلاس
# ----------------------------------
@login_required
def load_exam_types(request):
    class_id = request.GET.get('class_id')
    exams = ExamType.objects.filter(grades__school_class_id=class_id).distinct()
    data = [{'id': exam.id, 'name': exam.name} for exam in exams]
    return JsonResponse(data, safe=False)



    year = get_object_or_404(AcademicYear, pk=pk)
    if request.method == 'POST':
        year.delete()
        messages.success(request, "سال تحصیلی حذف شد ❌")
        return redirect('academic_year_list')
    return render(request, 'grades/academic/academic_year_confirm_delete.html', {'year': year})