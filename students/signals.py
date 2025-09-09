# import os
# from io import BytesIO
# import qrcode
# from django.core.files import File
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from students.models import StudentProfile
# from django.conf import settings

# @receiver(post_save, sender=StudentProfile)
# def generate_qr_for_new_student(sender, instance, created, **kwargs):
#     if created:  # فقط وقتی شاگرد جدید ساخته شد
#         # داده QR
#         qr_data = str(instance.attendance_token)
#         qr_img = qrcode.make(qr_data)

#         # ذخیره در BytesIO
#         stream = BytesIO()
#         qr_img.save(stream, format='PNG')
#         stream.seek(0)

#         # نام فایل
#         filename = f"student_{instance.id}.png"

#         # ذخیره در ImageField مدل و آپدیت دیتابیس
#         instance.qr_code.save(filename, File(stream), save=True)
