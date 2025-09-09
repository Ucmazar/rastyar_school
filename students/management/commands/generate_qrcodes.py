import os
import qrcode
from django.core.management.base import BaseCommand
from students.models import StudentProfile

class Command(BaseCommand):
    help = "Generate QR codes for all students (only attendance_token)"

    def handle(self, *args, **options):
        output_dir = "media/qrcodes/students"
        os.makedirs(output_dir, exist_ok=True)

        students = StudentProfile.objects.all()
        if not students.exists():
            self.stdout.write(self.style.WARNING("⚠️ No students found!"))
            return

        for student in students:
            qr_data = str(student.attendance_token)  # فقط توکن
            qr = qrcode.make(qr_data)
            file_path = os.path.join(output_dir, f"student_{student.id}_{student.user.full_name_display}.png")
            qr.save(file_path)
            self.stdout.write(
                self.style.SUCCESS(f"✅ QR generated for {student.user.full_name_display} (ID: {student.id})")
            )

        self.stdout.write(self.style.SUCCESS("🎉 All QR codes generated successfully!"))
