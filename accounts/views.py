# Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages

# Local apps
from .forms import CustomUserCreationForm, CustomUserLoginForm
from teachers.models import TeacherProfile


# ثبت‌نام
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # کاربر ذخیره می‌شود

            # ساخت پروفایل بر اساس نقش
            if user.role == "teacher":
                TeacherProfile.objects.get_or_create(user=user, defaults={"created_by": user})
            
            # لاگین خودکار
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")  # مسیر صفحه اصلی
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})

# ورود
def login_view(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect("home")
    else:
        form = CustomUserLoginForm()
    return render(request, "accounts/login.html", {"form": form})


# خروج
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


def permission_denied(request):
    # روش ۱: نمایش یک قالب
    return render(request, "accounts/permission_denied.html", status=403)
