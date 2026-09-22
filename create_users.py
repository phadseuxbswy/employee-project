import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User

accounts = [
    ('somchai', 'สมชาย', 'มั่นคง'),
    ('suchada', 'สุชาดา', 'งามตา'),
    ('kittisak', 'กิตติศักดิ์', 'รักเรียน'),
    ('wannapha', 'วรรณภา', 'ดีเสมอ'),
    ('arthit', 'อาทิตย์', 'สว่างวงศ์'),
    ('rawisara', 'รวิสรา', 'ใจเพชร'),
    ('thanaphon', 'ธนพล', 'ยอดเยี่ยม'),
    ('wilawan', 'วิลาวัณย์', 'สุขสม'),
    ('prasert', 'ประเสริฐ', 'บุญรอด'),
    ('pornthip', 'พรทิพย์', 'สุขใจ'),
    ('taenkhwan', 'แทนขวัญ', 'มูลลอด'),
]

for username, fname, lname in accounts:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': fname, 'last_name': lname}
    )
    user.set_password('12345678')
    user.first_name = fname
    user.last_name = lname
    user.save()
    print(f"สร้าง/อัปเดตผู้ใช้สำเร็จ: {username} ({fname} {lname})")

print("--- สร้างพนักงานครบทุกคนแล้ว ---")