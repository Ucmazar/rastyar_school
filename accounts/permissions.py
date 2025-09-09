from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse

# فرض: مدل CustomUser یک فیلد role دارد با مقادیر مثل: 'admin', 'teacher', 'student', 'parent'
# اگر نام فیلد در پروژه شما متفاوت است، آن را تغییر دهید.

DEFAULT_LOGIN_URL = 'login'  # دیگر بدون namespace
DEFAULT_DENIED_URL = 'permission_denied'


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest" or \
           request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


def role_required(allowed_roles=None, login_url=DEFAULT_LOGIN_URL, raise_forbidden=False):
    """
    دکوراتور جنریک برای نقش‌ها:
    - allowed_roles: لیستی از رشته‌های نقش مجاز (مثلاً ['admin','teacher'])
    - اگر کاربر لاگین نکرده باشد -> redirect به صفحه لاگین
    - اگر لاگین است ولی نقش مناسب ندارد -> یا 403 یا redirect به صفحه نامناسب بودن دسترسی
    - اگر is_superuser باشد همیشه اجازه دارد
    """
    allowed_roles = allowed_roles or []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect(f"{reverse(login_url)}?next={request.path}")

            # superuser bypass
            if getattr(user, "is_superuser", False):
                return view_func(request, *args, **kwargs)

            user_role = getattr(user, "role", None)  # assume CustomUser.role exists
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # اگر درخواست AJAX است، JSON با وضعیت 403 برمی‌گردانیم
            if _is_ajax(request):
                return JsonResponse({"detail": "forbidden"}, status=403)
            if raise_forbidden:
                return HttpResponseForbidden("شما دسترسی لازم را ندارید.")
            # در غیر اینصورت redirect به صفحه دسترسی غیرمجاز
            return redirect(DEFAULT_DENIED_URL)
        return _wrapped
    return decorator


def admin_required(view_func=None, login_url=DEFAULT_LOGIN_URL, raise_forbidden=False):
    if view_func:
        return role_required(['admin'], login_url=login_url, raise_forbidden=raise_forbidden)(view_func)
    return role_required(['admin'], login_url=login_url, raise_forbidden=raise_forbidden)


def teacher_required(view_func=None, login_url=DEFAULT_LOGIN_URL, raise_forbidden=False):
    if view_func:
        return role_required(['teacher'], login_url=login_url, raise_forbidden=raise_forbidden)(view_func)
    return role_required(['teacher'], login_url=login_url, raise_forbidden=raise_forbidden)


def student_required(view_func=None, login_url=DEFAULT_LOGIN_URL, raise_forbidden=False):
    if view_func:
        return role_required(['student'], login_url=login_url, raise_forbidden=raise_forbidden)(view_func)
    return role_required(['student'], login_url=login_url, raise_forbidden=raise_forbidden)


def parent_required(view_func=None, login_url=DEFAULT_LOGIN_URL, raise_forbidden=False):
    if view_func:
        return role_required(['parent'], login_url=login_url, raise_forbidden=raise_forbidden)(view_func)
    return role_required(['parent'], login_url=login_url, raise_forbidden=raise_forbidden)


def owner_or_admin(owner_attr='user', login_url=DEFAULT_LOGIN_URL, raise_forbidden=False):
    """
    اجازه فقط به صاحب آبجکت یا مدیر
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect(f"{reverse(login_url)}?next={request.path}")

            if getattr(user, "is_superuser", False) or getattr(user, "role", None) == "admin":
                return view_func(request, *args, **kwargs)

            # چک ساده: اگر view یک 'obj' در kwargs دارد که حاوی صفت owner_attr است
            obj = kwargs.get('obj', None)
            if obj and hasattr(obj, owner_attr):
                if getattr(obj, owner_attr) == user:
                    return view_func(request, *args, **kwargs)

            owner_id = kwargs.get(owner_attr) or kwargs.get(f"{owner_attr}_id")
            if owner_id and str(owner_id) == str(user.id):
                return view_func(request, *args, **kwargs)

            if _is_ajax(request):
                return JsonResponse({"detail": "forbidden"}, status=403)
            if raise_forbidden:
                return HttpResponseForbidden("شما اجازه ندارید این منبع را ببینید/ویرایش کنید.")
            return redirect(DEFAULT_DENIED_URL)
        return _wrapped
    return decorator


def json_role_required(allowed_roles=None):
    allowed_roles = allowed_roles or []
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({"detail": "authentication required"}, status=401)
            if getattr(user, "is_superuser", False):
                return view_func(request, *args, **kwargs)
            if getattr(user, "role", None) in allowed_roles:
                return view_func(request, *args, **kwargs)
            return JsonResponse({"detail": "forbidden"}, status=403)
        return _wrapped
    return decorator
