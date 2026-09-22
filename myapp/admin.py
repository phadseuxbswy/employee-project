from django.contrib import admin
# นำเข้า Models ทั้งหมดที่เรามี
from .models import Employee, Attendance, EmployeeRequest, Payroll

# นำ Employee และตารางอื่นๆ ไปแสดงในหน้า Admin
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(EmployeeRequest)
admin.site.register(Payroll)