# پایتون استاندارد
from io import BytesIO
from datetime import date
import pandas as pd
from django.db import transaction
from django.db.models import Q

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.templatetags.static import static

# Local apps
from accounts.models import CustomUser
from accounts.permissions import admin_required, role_required, owner_or_admin
from students.models import StudentProfile
from students.forms import StudentCreationForm, StudentExcelUploadForm
from grades.models import Grade, ExamType
from classes.models import SchoolClass
from subjects.models import Subject
from attendance.models import ExamAttendance

# Third-party
import qrcode
import jdatetime



User = get_user_model()
@login_required
def student_profile(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)

    # کلاس‌هایی که کاربر جاری ساخته
    user_classes = SchoolClass.objects.filter(created_by=request.user)
    selected_class_id = request.GET.get("class")
    selected_exam_id = request.GET.get("exam")

    selected_class = None
    selected_exam = None
    subjects = []
    exam_attendance = None  # 📌 اضافه شد

    # انتخاب کلاس
    if selected_class_id:
        try:
            selected_class = user_classes.get(id=selected_class_id)

            # گرفتن مضامین از گروه مضامین کلاس
            if selected_class.subject_group:
                subjects = selected_class.subject_group.subjects.all()
        except SchoolClass.DoesNotExist:
            messages.error(request, "صنف انتخابی معتبر نیست")

    # انتخاب امتحان
    exam_types_user = ExamType.objects.filter(created_by=request.user)
    if hasattr(request.user, "teacherprofile"):
        super_admins = User.objects.filter(is_superuser=True)
        admin_exams = ExamType.objects.filter(created_by__in=super_admins)
        exam_types_user = (exam_types_user | admin_exams).distinct()

    if selected_exam_id:
        try:
            selected_exam_id = int(selected_exam_id)
            selected_exam = exam_types_user.get(id=selected_exam_id)

            # 📌 گرفتن یا ساختن حاضری امتحان
            if selected_class:
                exam_attendance, created = ExamAttendance.objects.get_or_create(
                    student=student,
                    school_class=selected_class,
                    exam_type=selected_exam,
                    defaults={
                        "recorded_by": request.user,
                    }
                )
        except (ValueError, ExamType.DoesNotExist):
            selected_exam = None
            messages.warning(request, "امتحان انتخابی معتبر نیست")

    context = {
        "student": student,
        "user_classes": user_classes,
        "selected_class": selected_class,
        "exam_types": exam_types_user,
        "selected_exam": selected_exam,
        "subjects": subjects,
        "exam_attendance": exam_attendance,  # 📌 فرستادن به قالب
    }
    return render(request, "students/profile.html", context)


User = get_user_model()

@login_required
@owner_or_admin(owner_attr="user")
def grade_update_ajax(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        student_id = request.POST.get("student_id")
        class_id = request.POST.get("class_id")
        exam_id = request.POST.get("exam_id")
        subject_id = request.POST.get("subject_id")
        score = request.POST.get("score")

        try:
            # اعتبارسنجی اولیه
            if not student_id or not class_id or not exam_id:
                return JsonResponse({"success": False, "message": "اطلاعات شاگرد، صنف یا امتحان کافی نیست."})

            student = StudentProfile.objects.get(id=student_id)
            school_class = SchoolClass.objects.get(id=class_id)

            # تبدیل exam_id به int
            try:
                exam_id = int(exam_id)
            except (TypeError, ValueError):
                return JsonResponse({"success": False, "message": "امتحان انتخابی معتبر نیست."})

            # گرفتن امتحان با بررسی دسترسی
            if hasattr(request.user, "teacherprofile"):
                super_admins = User.objects.filter(is_superuser=True)
                exam_qs = ExamType.objects.filter(
                    Q(id=exam_id) & (Q(created_by=request.user) | Q(created_by__in=super_admins))
                )
            else:
                exam_qs = ExamType.objects.filter(id=exam_id, created_by=request.user)

            exam = exam_qs.first()
            if not exam:
                return JsonResponse({"success": False, "message": "امتحان پیدا نشد یا دسترسی ندارید."})

            # ------------------ ثبت یا بروزرسانی نمره ------------------
            if subject_id and score is not None and score != '':
                subject = Subject.objects.filter(
                    id=subject_id,
                    subjectgroup__schoolclass=school_class  # بررسی تعلق مضمون به کلاس
                ).first()
                if not subject:
                    return JsonResponse({"success": False, "message": "مضمون برای این صنف معتبر نیست."})

                try:
                    score_float = float(score)
                except ValueError:
                    score_float = 0

                Grade.objects.update_or_create(
                    student=student,
                    school_class=school_class,
                    subject=subject,
                    exam_type=exam,
                    defaults={'score': score_float, 'created_by': request.user}
                )

            return JsonResponse({"success": True})

        except StudentProfile.DoesNotExist:
            return JsonResponse({"success": False, "message": "شاگرد پیدا نشد."})
        except SchoolClass.DoesNotExist:
            return JsonResponse({"success": False, "message": "صنف پیدا نشد."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "درخواست نامعتبر"})




@login_required
@owner_or_admin(owner_attr="user")
def attendance_update_ajax(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        student_id = request.POST.get("student_id")
        class_id = request.POST.get("class_id")
        exam_id = request.POST.get("exam_id")

        # داده‌های حضور و غیاب
        present = request.POST.get("present")
        absent  = request.POST.get("absent")
        sick    = request.POST.get("sick")
        leave   = request.POST.get("leave")

        try:
            # اعتبارسنجی اولیه
            if not student_id or not class_id or not exam_id:
                return JsonResponse({"success": False, "message": "اطلاعات شاگرد، صنف یا امتحان کافی نیست."})

            student = StudentProfile.objects.get(id=student_id)
            school_class = SchoolClass.objects.get(id=class_id)

            # تبدیل exam_id به int
            try:
                exam_id = int(exam_id)
            except (TypeError, ValueError):
                return JsonResponse({"success": False, "message": "امتحان انتخابی معتبر نیست."})

            # بررسی دسترسی به امتحان
            if hasattr(request.user, "teacherprofile"):
                super_admins = User.objects.filter(is_superuser=True)
                exam_qs = ExamType.objects.filter(
                    Q(id=exam_id) & (Q(created_by=request.user) | Q(created_by__in=super_admins))
                )
            else:
                exam_qs = ExamType.objects.filter(id=exam_id, created_by=request.user)

            exam = exam_qs.first()
            if not exam:
                return JsonResponse({"success": False, "message": "امتحان پیدا نشد یا دسترسی ندارید."})

            # تبدیل مقادیر خالی به 0 و اطمینان از int بودن
            present = int(present or 0)
            absent  = int(absent or 0)
            sick    = int(sick or 0)
            leave   = int(leave or 0)

            # ثبت یا بروزرسانی حضور و غیاب
            ExamAttendance.objects.update_or_create(
                student=student,
                school_class=school_class,
                exam_type=exam,
                defaults={
                    "present_days": present,
                    "absent_days": absent,
                    "sick_days": sick,
                    "leave_days": leave,
                    "recorded_by": request.user
                }
            )

            return JsonResponse({"success": True})

        except StudentProfile.DoesNotExist:
            return JsonResponse({"success": False, "message": "شاگرد پیدا نشد."})
        except SchoolClass.DoesNotExist:
            return JsonResponse({"success": False, "message": "صنف پیدا نشد."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "درخواست نامعتبر"})



@login_required
@role_required(['admin', 'teacher'])
def student_list(request):
    user = request.user

    # شاگردانی که کاربر ایجاد کرده
    students = StudentProfile.objects.filter(created_by=user)

    # فیلتر کردن امتحانات بر اساس نقش کاربر
    if user.role == "teacher":
        # امتحانات خودش
        user_exams = ExamType.objects.filter(created_by=user)
        # امتحانات سوپرادمین‌ها
        super_admins = User.objects.filter(is_superuser=True)
        admin_exams = ExamType.objects.filter(created_by__in=super_admins)
        exam_types = (user_exams | admin_exams).distinct()
    elif user.role == "admin":
        # فقط امتحانات خودش
        exam_types = ExamType.objects.filter(created_by=user)
    else:
        exam_types = ExamType.objects.none()  # سایر نقش‌ها امتحانی نمی‌بینند

    context = {
        'students': students,
        'exam_types': exam_types,
    }
    return render(request, "students/student_list.html", context)





@login_required
def create_student(request):
    if request.method == "POST":
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.created_by = request.user
            student.save()
            form.save_m2m()  # برای فیلدهای ManyToMany مثل subjects
            return redirect("student_list")
    else:
        form = StudentCreationForm()
    return render(request, "students/create_student.html", {"form": form, "student": None})


@login_required
def edit_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)

    if request.method == "POST":
        form = StudentCreationForm(request.POST, instance=student)
        if form.is_valid():
            student_profile = form.save(commit=False)

            # آپدیت فیلدهای پروفایل
            student_profile.father_name = form.cleaned_data.get("father_name", student_profile.father_name)
            student_profile.grandfather_name = form.cleaned_data.get("grandfather_name", student_profile.grandfather_name)
            student_profile.student_number = form.cleaned_data.get("student_number", student_profile.student_number)
            student_profile.phone = form.cleaned_data.get("phone", student_profile.phone)
            student_profile.address = form.cleaned_data.get("address", student_profile.address)
            student_profile.date_of_birth = form.cleaned_data.get("date_of_birth", student_profile.date_of_birth)

            # آپدیت فیلدهای کاربر
            user = student_profile.user
            user.first_name = form.cleaned_data.get("first_name", user.first_name)
            user.last_name = form.cleaned_data.get("last_name", user.last_name)
            user.email = form.cleaned_data.get("email", user.email)
            user.save()

            student_profile.save()
            form.save_m2m()
            return redirect("student_list")
    else:
        form = StudentCreationForm(
            instance=student,
            initial={
                "first_name": student.user.first_name,
                "last_name": student.user.last_name,
            })
        

    return render(request, "students/create_student.html", {"form": form, "student": student})

@login_required
def delete_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    
    if request.method == "POST":
        if student.qr_code:
            student.qr_code.delete(save=False)
        student.delete()
        return redirect("student_list")
    
    return render(request, "students/confirm_delete.html", {"student": student})





@login_required
def upload_students(request):
    if request.method == "POST" and request.FILES.get("file"):
        excel_file = request.FILES["file"]

        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            messages.error(request, f"خطا در خواندن فایل: {str(e)}")
            return redirect("upload_students")

        required_columns = ["نام", "نام پدر", "نام پدر کلان", "شماره اساس"]
        for col in required_columns:
            if col not in df.columns:
                messages.error(request, f"ستون '{col}' در فایل اکسل موجود نیست.")
                return redirect("upload_students")

        success_count = 0
        error_rows = []

        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    username = str(row["شماره اساس"])  # تبدیل به رشته
                    first_name = str(row["نام"])        # تبدیل به رشته
                    father_name = str(row.get("نام پدر", ""))
                    grandfather_name = str(row.get("نام پدر کلان", ""))

                    user, created = CustomUser.objects.get_or_create(
                        username=username,
                        defaults={
                            "first_name": first_name,
                            "last_name": "",  # نام خانوادگی خالی
                        }
                    )

                    profile, created = StudentProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            "father_name": father_name,
                            "grandfather_name": grandfather_name,
                            "student_number": username,
                            "created_by": request.user,  # ✅ اینجا فیلد created_by تنظیم شد
                        }
                    )
                    success_count += 1

            except Exception as e:
                error_rows.append(f"ردیف {index + 2} : {str(e)}")

        if success_count:
            messages.success(request, f"{success_count} شاگرد با موفقیت اضافه شدند.")
        if error_rows:
            for err in error_rows:
                messages.error(request, f"خطا در پردازش فایل: {err}")

        return redirect("upload_students")

    return render(request, "students/upload_students.html")



@login_required
def student_report_card(request, pk):
    # گرفتن شاگرد
    student = get_object_or_404(StudentProfile, id=pk)

    # گرفتن لیست id امتحانات انتخاب شده از فرم
    selected_exam_ids = request.GET.getlist('exams')  # ['1', '2', '5'] به صورت str
    if selected_exam_ids:
        exam_types = ExamType.objects.filter(id__in=selected_exam_ids)
    else:
        exam_types = ExamType.objects.none()  # هیچ امتحانی انتخاب نشده



    # گرفتن نمرات شاگرد فقط برای امتحانات انتخاب شده
    grades = student.grades.filter(exam_type__in=exam_types)

    # گرفتن کلاس‌های شاگرد
    school_classes = student.classes.all()
    school_class = school_classes.first() if school_classes.exists() else None

    # گرفتن مضامین فقط از گروه‌هایی که توسط کاربر جاری ساخته شده‌اند
    subjects = Subject.objects.filter(groups__created_by=request.user)

    # تاریخ امروز
    today = date.today()
    shamsi_year_approx = today.year - 621
    hijri_year_approx = int((today.year - 622) * 33 / 32)

    # محاسبه اوسط هر امتحان
    exam_totals = []
    for exam in exam_types:
        scores = grades.filter(exam_type=exam).values_list('score', flat=True)
        total = sum(scores)
        count = len(scores) or 1
        avg = total / count

        # تعیین درجه هر امتحان
        if avg >= 90:
            exam_grade = 'الف'
        elif avg >= 75:
            exam_grade = 'ب'
        elif avg >= 60:
            exam_grade = 'ج'
        elif avg >= 50:
            exam_grade = 'د'
        else:
            exam_grade = 'هـ'

        exam_totals.append({
            'exam': exam.name,
            'total': total,
            'avg': avg,
            'grade': exam_grade
        })

    # آماده کردن دیکشنری نمرات برای هر مضمون
    subject_scores = []
    for subject in subjects:
        scores = []
        total = 0
        for exam in exam_types:
            grade = grades.filter(subject=subject, exam_type=exam).first()
            score = grade.score if grade else 0
            scores.append(score)
            total += score
        subject_scores.append({
            'subject': subject.name,
            'scores': scores,
            'total': total
        })

    # تعداد ستون‌ها برای ردیف‌های جمع/فیصدی/نتیجه
    colspan_count = exam_types.count() + 1  # +1 برای ستون "مجموع"

    # محاسبه اوسط نمره کل
    total_scores = [s['total'] for s in subject_scores]
    avg_score = sum(total_scores) / len(total_scores) if total_scores else 0

    # تعیین درجه
    if avg_score >= 90:
        grade_letter = 'الف'
    elif avg_score >= 75:
        grade_letter = 'ب'
    elif avg_score >= 60:
        grade_letter = 'ج'
    elif avg_score >= 50:
        grade_letter = 'د'
    else:
        grade_letter = 'هـ'

    context = {
        'student': student,
        'school_class': school_class,
        'exam_types': exam_types,
        'subject_scores': subject_scores,
        'avg_score': avg_score,
        'grade_letter': grade_letter,
        'today': today,
        'shamsi_year_approx': shamsi_year_approx,
        'hijri_year_approx': hijri_year_approx,
        'colspan_count': colspan_count,
        'exam_totals': exam_totals,
    }

    return render(request, 'shared/student_report_card.html', context)


@login_required
def download_student_qr(request, student_id):
    student = StudentProfile.objects.get(id=student_id)

    # محتوای QR (مثلاً نمبر اساس یا ترکیب چند فیلد)
    qr_data = f"Student: {student.user.first_name} {student.user.last_name} | Number: {student.student_number}"

    # ساخت QR
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    # برگرداندن به صورت فایل دانلود
    response = HttpResponse(buffer, content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="student_{student.id}_qr.png"'
    return response



