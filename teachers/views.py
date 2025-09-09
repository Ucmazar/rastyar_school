from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TeacherForm, TeacherProfileForm
from .models import TeacherProfile
from accounts.permissions import admin_required, owner_or_admin


@login_required
@admin_required
def teacher_list(request):
    user = request.user
    # نمایش تمام معلمانی که توسط کاربر جاری ساخته شده‌اند
    teachers = TeacherProfile.objects.filter(created_by=user)
    return render(request, "teachers/teacher_list.html", {"teachers": teachers})

@login_required
def create_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, creator=request.user)
        if form.is_valid():
            form.save()
            return redirect("teacher_list")
    else:
        form = TeacherForm(creator=request.user)
    return render(request, "teachers/create_teacher.html", {"form": form})

@login_required
def edit_teacher(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    user_instance = teacher.user
    if request.method == "POST":
        form = TeacherForm(request.POST, instance=teacher, user_instance=user_instance, creator=request.user)
        if form.is_valid():
            form.save(instance=teacher)
            messages.success(request, "معلم با موفقیت بروزرسانی شد.")
            return redirect("teacher_list")
    else:
        form = TeacherForm(instance=teacher, user_instance=user_instance, creator=request.user)
    return render(request, "teachers/create_teacher.html", {"form": form, "teacher": teacher})


@login_required
def delete_teacher(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    if request.method == "POST":
        user = teacher.user
        teacher.delete()  # حذف پروفایل
        user.delete()     # حذف کاربر مربوطه
        messages.success(request, "معلم با موفقیت حذف شد.")
        return redirect("teacher_list")
    return render(request, "teachers/confirm_delete.html", {"teacher": teacher})



@login_required
def teacher_profile(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    return render(request, "teachers/profile.html", {"teacher": teacher})



@login_required
def teacher_dashboard_or_profile(request):
    user = request.user
    if user.role != "teacher":
        return redirect("home")  # یا صفحه اصلی مناسب

    # بررسی پروفایل معلم
    teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)

    # اگر پروفایل جدید ساخته شده یا فیلدها ناقص هستند → هدایت به فرم تکمیل
    if created or not teacher_profile.father_name or not teacher_profile.date_of_birth:
        return redirect("teacher_profile_edit")  # مسیر فرم تکمیل پروفایل

    # اگر همه چیز تکمیل است → هدایت به داشبورد یا صفحه اصلی معلم
    return redirect("teacher_dashboard")  




@login_required
def teacher_profile_edit(request):
    user = request.user

    if user.role != "teacher":
        return redirect("home")  # یا صفحه مناسب دیگر

    # گرفتن پروفایل معلم یا ایجاد اگر وجود ندارد
    teacher_profile, _ = TeacherProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = TeacherProfileForm(request.POST, instance=teacher_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # به‌روزرسانی نام و تخلص کاربر
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            user.save()

            profile.save()
            return redirect("home")  # یا صفحه بعد از تکمیل پروفایل
    else:
        # مقداردهی اولیه فیلدهای نام و تخلص در فرم
        initial = {
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        form = TeacherProfileForm(instance=teacher_profile, initial=initial)

    return render(request, "teachers/profile_form.html", {"form": form})
