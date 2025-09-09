# accounts/templatetags/jformat.py
from django import template
from khayyam import JalaliDate, JalaliDatetime
import datetime

register = template.Library()

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
def to_persian_numbers(value):
    s = str(value)
    out = []
    for ch in s:
        if ch.isdigit():
            out.append(PERSIAN_DIGITS[int(ch)])
        else:
            out.append(ch)
    return "".join(out)

@register.filter(name="jformat")
def jformat(value, fmt="%Y/%m/%d"):
    """
    میلادی -> جلالی (افغانستان) + اعداد فارسی
    """
    if not value:
        return ""

    # اگر رشته باشد تلاش می‌کنیم ISO/یا %Y-%m-%d تبدیل کنیم
    if isinstance(value, str):
        parsed = None
        for pattern in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                parsed = datetime.datetime.strptime(value, pattern)
                break
            except ValueError:
                continue
        if parsed is None:
            try:
                parsed = datetime.datetime.fromisoformat(value)
            except Exception:
                return to_persian_numbers(value)
        value = parsed

    # تاریخ/زمان را جلالی کن
    if isinstance(value, datetime.datetime):
        jd = JalaliDatetime(value)
        formatted = jd.strftime(fmt)
        return to_persian_numbers(formatted)

    if isinstance(value, datetime.date):
        jd = JalaliDate(value)
        formatted = jd.strftime(fmt)
        return to_persian_numbers(formatted)

    # هر چیز دیگر را فقط اعدادش را فارسی کن
    return to_persian_numbers(value)
