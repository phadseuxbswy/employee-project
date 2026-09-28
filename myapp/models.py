from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

TITLE_CHOICES = [
    ('นาย', 'นาย'),
    ('นาง', 'นาง'),
    ('นางสาว', 'นางสาว'),
]

GENDER_CHOICES = [
    ('M', 'ชาย'),
    ('F', 'หญิง'),
    ('O', 'อื่นๆ'),
]

DEPT_CHOICES = [
    ('IT', 'ไอที'),
    ('HR', 'บุคคล'),
    ('ACC', 'บัญชี'),
    ('MKT', 'การตลาด'),
    ('SALES', 'ฝ่ายขาย'),
    ('PURCHASE', 'จัดซื้อ'),
    ('CS', 'บริการลูกค้า'),
    ('MGMT', 'บริหาร'),
]

STATUS_CHOICES = [
    ('active', 'ประจำ (Permanent)'),
    ('probation', 'ทดลองงาน (Probation)'),
    ('resigned', 'ลาออก (Resigned)'),
]

BANK_CHOICES = [
    ('kbank', 'ธนาคารกสิกรไทย (KBANK)'),
    ('scb', 'ธนาคารไทยพาณิชย์ (SCB)'),
    ('bbl', 'ธนาคารกรุงเทพ (BBL)'),
    ('ktb', 'ธนาคารกรุงไทย (KTB)'),
    ('krungsri', 'ธนาคารกรุงศรีอยุธยา (BAY)'),
    ('ttb', 'ธนาคารทหารไทยธนชาต (TTB)'),
    ('other', 'อื่นๆ'),
]

class Employee(models.Model):
    # 🟢 เพิ่มฟิลด์รหัสพนักงาน (ไม่ซ้ำกัน และปล่อยว่างได้ตอนบันทึกรอบแรกเพื่อให้ระบบ generate ให้)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="รหัสพนักงาน")
    
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='นาย', verbose_name="คำนำหน้าชื่อ")
    first_name = models.CharField(max_length=100, verbose_name="ชื่อ")
    last_name = models.CharField(max_length=100, verbose_name="นามสกุล")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="เพศ")
    birth_date = models.DateField(verbose_name="วัน-เดือน-ปี เกิด (YYYY-MM-DD)")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="เงินเดือน")
    department = models.CharField(max_length=20, choices=DEPT_CHOICES, verbose_name="แผนก")
    position = models.CharField(max_length=100, null=True, blank=True, verbose_name="ตำแหน่ง")
    hire_date = models.DateField(null=True, blank=True, verbose_name="วันที่เริ่มทำงาน")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="สถานะพนักงาน")
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="เบอร์โทรศัพท์")
    email = models.EmailField(blank=True, null=True, verbose_name="อีเมล") # เพิ่มฟิลด์อีเมลรองรับไว้แล้ว
    address = models.TextField(blank=True, null=True, verbose_name="ที่อยู่")
    bank_name = models.CharField(max_length=50, choices=BANK_CHOICES, null=True, blank=True, verbose_name="ชื่อธนาคาร")
    bank_account = models.CharField(max_length=50, null=True, blank=True, verbose_name="เลขบัญชีธนาคาร")
    
    photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True, verbose_name="รูปภาพประจำตัว")

    # 🟢 ฟังก์ชันสร้างรหัสพนักงานอัตโนมัติ (เช่น EMP001)
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not self.employee_id:
            # นับจำนวนพนักงานทั้งหมดในระบบเพื่อรันเลขต่อเนื่อง (เช่น EMP001, EMP002, ...)
            total_count = Employee.objects.count()
            self.employee_id = f"EMP{total_count:03d}"
            Employee.objects.filter(pk=self.pk).update(employee_id=self.employee_id)
    def __str__(self):
        return f"{self.employee_id} - {self.title}{self.first_name} {self.last_name}"


# ================= 1. ระบบบันทึกเวลาทำงาน =================
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="พนักงาน")
    date = models.DateField(default=timezone.now, verbose_name="วันที่")
    check_in = models.TimeField(null=True, blank=True, verbose_name="เวลาเข้างาน")
    check_out = models.TimeField(null=True, blank=True, verbose_name="เวลาออกงาน")
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, verbose_name="ชั่วโมง OT")

    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', '-check_in']

    def __str__(self):
        return f"{self.employee} - {self.date}"


# ================= 2. ระบบอนุมัติคำขอ (ลา / OT / เบิกเงิน) =================
class EmployeeRequest(models.Model):
    REQUEST_TYPES = [
        ('leave', 'ขอลาหยุด'),
        ('ot', 'ขอทำงานล่วงเวลา (OT)'),
        ('expense', 'ขอเบิกค่าใช้จ่าย'),
    ]
    STATUS_CHOICES = [
        ('pending', 'รออนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('rejected', 'ไม่อนุมัติ'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="พนักงาน")
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, verbose_name="ประเภทคำขอ")
    title = models.CharField(max_length=200, verbose_name="หัวข้อ / รายละเอียด")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="จำนวนเงิน หรือ จำนวนชั่วโมง")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ส่งคำขอ")
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True, verbose_name="ไฟล์แนบ (ใบรับรองแพทย์/ใบเสร็จ)")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.employee}"


# ================= 3. ระบบคำนวณเงินเดือน (Payroll) =================
class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="พนักงาน")
    month = models.IntegerField(verbose_name="เดือน")
    year = models.IntegerField(verbose_name="ปี")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="เงินเดือนพื้นฐาน")
    ot_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="ค่า OT")
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="หักประกันสังคม (5%)")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="หักภาษี ณ ที่จ่าย")
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="เงินเดือนสุทธิ")

    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"เงินเดือน {self.employee} ({self.month}/{self.year})"
    

# ================= 4. ระบบแผนกและจัดการสิทธิ์ =================
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="ชื่อแผนก")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')

    def __str__(self):
        return self.name


# ================= 5. ระบบ Audit Log =================
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="ผู้กระทำ")
    action = models.CharField(max_length=255, verbose_name="รายละเอียดการกระทำ")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"