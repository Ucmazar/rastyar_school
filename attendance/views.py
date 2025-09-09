from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from students.models import StudentProfile
from .models import Attendance
from classes.models import SchoolClass
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from .models import ExamAttendance
from .forms import ExamAttendanceForm
from grades.models import ExamType



@login_required
def mark_attendance(request):
    if request.method == "POST":
        qr_token = request.POST.get("attendance_token")  # از QR اسکن شده
        school_class_id = request.POST.get("school_class")  # کلاس انتخاب شده یا ثابت
        student = get_object_or_404(StudentProfile, attendance_token=qr_token)
        school_class = get_object_or_404(SchoolClass, id=school_class_id)

        # بررسی اینکه رکورد قبلی وجود دارد یا نه
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            school_class=school_class,
            date=timezone.now().date(),
            defaults={'recorded_by': request.user}
        )

        if not created:
            return HttpResponse("✅ حضور قبلاً ثبت شده بود!")

        return HttpResponse(f"✅ حضور ثبت شد برای {student.user.full_name_display}")

    # فرم ساده برای تست
    school_classes = SchoolClass.objects.all()
    return render(request, "attendance/mark_attendance.html", {"school_classes": school_classes})

@login_required
def scan_attendance_page(request):
    return render(request, "attendance/scan_attendance.html")



# ترکیب csrf_exempt با login_required
def login_required_json(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not logged in"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from students.models import StudentProfile
from .models import Attendance
from classes.models import SchoolClass
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

@login_required
def mark_attendance(request):
    if request.method == "POST":
        qr_token = request.POST.get("attendance_token")  # از QR اسکن شده
        school_class_id = request.POST.get("school_class")  # کلاس انتخاب شده یا ثابت
        student = get_object_or_404(StudentProfile, attendance_token=qr_token)
        school_class = get_object_or_404(SchoolClass, id=school_class_id)

        # بررسی اینکه رکورد قبلی وجود دارد یا نه
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            school_class=school_class,
            date=timezone.now().date(),
            defaults={'recorded_by': request.user}
        )

        if not created:
            return HttpResponse("✅ حضور قبلاً ثبت شده بود!")

        return HttpResponse(f"✅ حضور ثبت شد برای {student.user.full_name_display}")

    # فرم ساده برای تست
    school_classes = SchoolClass.objects.all()
    return render(request, "attendance/mark_attendance.html", {"school_classes": school_classes})

@login_required
def scan_attendance_page(request):
    return render(request, "attendance/scan_attendance.html")


# ترکیب csrf_exempt با login_required
def login_required_json(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not logged in"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


@csrf_exempt
@login_required_json
def mark_attendance_qr(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    try:
        data = json.loads(request.body)
        token = data.get("attendance_token")
        if not token:
            return JsonResponse({"error": "Missing token"}, status=400)
        
        try:
            student = StudentProfile.objects.get(attendance_token=token)
        except StudentProfile.DoesNotExist:
            return JsonResponse({"error": "Invalid token"}, status=404)
        
        # 🔹 پیدا کردن کلاس شاگرد (اولین کلاس موجود)
        school_class = student.classes.first()
        if not school_class:
            return JsonResponse({"error": "Student has no assigned class"}, status=400)
        
        # ثبت حضور یا آپدیت کردن آن
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            school_class=school_class,
            date=timezone.now().date(),
            defaults={
                'recorded_by': request.user,
                'timestamp': timezone.now()  # آپدیت زمان ثبت
            }
        )

        return JsonResponse({"status": "success", "student": student.user.get_full_name()})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def latest_attendance(request):
    today = timezone.now().date()
    records = Attendance.objects.filter(date=today).select_related("student", "school_class").order_by("-timestamp")[:20]
    data = [
        {
            "student": record.student.user.get_full_name(),
            "class": record.school_class.name,
            "time": record.timestamp.strftime("%H:%M:%S"),
            "recorded_by": record.recorded_by.username if record.recorded_by else "سیستم"
        }
        for record in records
    ]
    return JsonResponse({"records": data})





@login_required
def exam_attendance_create(request, class_id, exam_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    exam_type = get_object_or_404(ExamType, id=exam_id)
    students = school_class.students.all()

    if request.method == 'POST':
        for student in students:
            present = int(request.POST.get(f'present_{student.id}', 0))
            absent = int(request.POST.get(f'absent_{student.id}', 0))
            sick = int(request.POST.get(f'sick_{student.id}', 0))
            leave = int(request.POST.get(f'leave_{student.id}', 0))

            obj, created = ExamAttendance.objects.update_or_create(
                student=student,
                school_class=school_class,
                exam_type=exam_type,
                defaults={
                    'present_days': present,
                    'absent_days': absent,
                    'sick_days': sick,
                    'leave_days': leave,
                    'recorded_by': request.user
                }
            )
        return redirect('exam_attendance_list', class_id=school_class.id, exam_id=exam_type.id)

    # GET
    existing_attendance = {ea.student.id: ea for ea in ExamAttendance.objects.filter(
        school_class=school_class, exam_type=exam_type
    )}

    context = {
        'school_class': school_class,
        'exam_type': exam_type,
        'students': students,
        'existing_attendance': existing_attendance,
    }
    return render(request, 'attendance/exam_attendance_form.html', context)



@login_required
def exam_attendance_edit(request, student_id, exam_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    exam = get_object_or_404(ExamType, id=exam_id)

    # اگر رکورد قبلاً موجود باشد، برای آپدیت instance می‌دهیم
    attendance, created = ExamAttendance.objects.get_or_create(
        student=student,
        exam_type=exam,
        defaults={'present_days': 0, 'absent_days': 0, 'sick_days': 0, 'leave_days': 0}
    )

    if request.method == 'POST':
        form = ExamAttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('students:student_detail', pk=student.id)  # یا هر صفحه‌ای که می‌خوای بعد از ذخیره بروید
    else:
        form = ExamAttendanceForm(instance=attendance)

    context = {
        'form': form,
        'student': student,
        'exam': exam,
    }
    return render(request, 'attendance/exam_attendance_form.html', context)
