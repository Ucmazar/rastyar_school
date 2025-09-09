# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Local apps
from .models import Subject
from .forms import SubjectForm
from .models import SubjectGroup
from .forms import SubjectGroupForm

# --------------------------
# لیست مضامین
# --------------------------
User = get_user_model()
@login_required
def subject_list(request):
    user = request.user

    # حالت پیش‌فرض → فقط مضامینی که خود کاربر ایجاد کرده
    subjects = Subject.objects.filter(created_by=user)

    # اگر کاربر معلم باشد → علاوه بر مضامینی که خودش ساخته،
    # مضامینی که توسط سوپرادمین‌ها ساخته شده هم ببیند
    if hasattr(user, "teacherprofile"):  # چک می‌کنیم آیا پروفایل معلم دارد
        super_admins = User.objects.filter(is_superuser=True)
        subjects = Subject.objects.filter(created_by__in=list(super_admins) + [user])

    return render(request, "subjects/subject_list.html", {"subjects": subjects})

# --------------------------
# ایجاد مضمون
# --------------------------
@login_required
def subject_create(request):
    if request.method == "POST":
        form = SubjectForm(request.POST, creator=request.user)
        if form.is_valid():
            form.save()
            return redirect("subject_list")
    else:
        form = SubjectForm(creator=request.user)
    return render(request, "subjects/subject_form.html", {"form": form})

# --------------------------
# ویرایش مضمون
# --------------------------
@login_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect("subject_list")
    else:
        form = SubjectForm(instance=subject)
    return render(request, "subjects/subject_form.html", {"form": form})

# --------------------------
# حذف مضمون
# --------------------------
@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk, created_by=request.user)
    if request.method == "POST":
        subject.delete()
        return redirect("subject_list")
    return render(request, "subjects/subject_confirm_delete.html", {"subject": subject})






# --------------------------
# لیست گروه‌ها
# --------------------------
@login_required
def subjectgroup_list(request):
    user = request.user

    # پیش‌فرض: فقط گروه‌هایی که خود کاربر ساخته
    groups = SubjectGroup.objects.filter(created_by=user)

    # اگر کاربر معلم است → گروه‌های سوپرادمین‌ها + خودش
    if hasattr(user, "teacherprofile"):
        super_admins = User.objects.filter(is_superuser=True)
        groups = SubjectGroup.objects.filter(created_by__in=list(super_admins) + [user])

    return render(request, "subjects/subjectgroup_list.html", {"groups": groups})

# --------------------------
# ایجاد گروه
# --------------------------
@login_required
def subjectgroup_create(request):
    if request.method == "POST":
        form = SubjectGroupForm(request.POST, user=request.user)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            form.save_m2m()  # ذخیره ManyToManyField
            return redirect("subjectgroup_list")
    else:
        form = SubjectGroupForm(user=request.user)

    return render(request, "subjects/subjectgroup_form.html", {"form": form})
# --------------------------
# ویرایش گروه
# --------------------------
@login_required
def subjectgroup_update(request, pk):
    group = get_object_or_404(SubjectGroup, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = SubjectGroupForm(request.POST, instance=group, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("subjectgroup_list")
    else:
        form = SubjectGroupForm(instance=group, user=request.user)
    return render(request, "subjects/subjectgroup_form.html", {"form": form})

# --------------------------
# حذف گروه
# --------------------------
@login_required
def subjectgroup_delete(request, pk):
    group = get_object_or_404(SubjectGroup, pk=pk, created_by=request.user)
    if request.method == "POST":
        group.delete()
        return redirect("subjectgroup_list")
    return render(request, "subjects/subjectgroup_confirm_delete.html", {"group": group})
