from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# นำเข้า Models และ Forms
from .models import Employee, Attendance, EmployeeRequest, Payroll
from .forms import EmployeeForm, UserProfileForm, CustomRegisterForm

# ================= ฟังก์ชันตรวจสอบสิทธิ์ (Admin Only) =================
def is_admin(user):
    return user.is_staff
# =============================================================

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def index(request):
    query = request.GET.get('q', '')
    employees = Employee.objects.all().order_by('-id')
    
    if query:
        dept_code = None
        q_lower = query.strip().lower()
        
        if 'ไอที' in q_lower or 'it' in q_lower:
            dept_code = 'IT'
        elif 'บุคคล' in q_lower or 'hr' in q_lower:
            dept_code = 'HR'
        elif 'บัญชี' in q_lower or 'acc' in q_lower:
            dept_code = 'ACC'
        elif 'การตลาด' in q_lower or 'mkt' in q_lower:
            dept_code = 'MKT'
        elif 'ขาย' in q_lower or 'sales' in q_lower:
            dept_code = 'SALES'
        elif 'จัดซื้อ' in q_lower or 'purchase' in q_lower:
            dept_code = 'PURCHASE'
        elif 'บริการ' in q_lower or 'customer' in q_lower or 'cs' in q_lower:
            dept_code = 'CS'
        elif 'บริหาร' in q_lower or 'mgmt' in q_lower:
            dept_code = 'MGMT'

        search_filter = (
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(position__icontains=query)
        )
        
        if dept_code:
            search_filter |= Q(department=dept_code)
        else:
            search_filter |= Q(department__icontains=query)

        employees = employees.filter(search_filter)

    paginator = Paginator(employees, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index.html', {'page_obj': page_obj, 'query': query})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
@permission_required('myapp.add_employee', raise_exception=True)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มข้อมูลพนักงานสำเร็จ')
            return redirect('index')
    else:
        form = EmployeeForm()
    return render(request, 'form_view.html', {'form': form, 'title': 'เพิ่มพนักงาน'})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
@permission_required('myapp.change_employee', raise_exception=True)
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลสำเร็จ')
            return redirect('index')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'form_view.html', {'form': form, 'title': 'แก้ไขพนักงาน'})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
@permission_required('myapp.delete_employee', raise_exception=True)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'ลบข้อมูลสำเร็จ')
        return redirect('index')
    return render(request, 'delete.html', {'employee': employee})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบเพื่อใช้งาน')
            return redirect('login') 
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# 🌟 อัปเดตฟังก์ชันนี้สำหรับรับไฟล์รูปภาพ 🌟
@login_required
def profile(request):
    # 1. หาข้อมูล Employee ที่ชื่อและนามสกุลตรงกับ User ที่กำลังล็อกอิน
    employee = Employee.objects.filter(first_name=request.user.first_name, last_name=request.user.last_name).first()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            
            # 2. เซฟรูปลง Employee ที่หาเจอ
            if 'photo' in request.FILES and employee:
                employee.photo = request.FILES['photo']
                employee.save()
                
            messages.success(request, 'อัปเดตโปรไฟล์และรูปภาพสำเร็จ')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    # 3. แนบ employee ไปให้หน้าเว็บใช้งานด้วย
    return render(request, 'profile.html', {'form': form, 'employee': employee})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'detail.html', {'employee': employee})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def dashboard(request):
    total_employees = Employee.objects.count()
    avg_salary = Employee.objects.aggregate(Avg('salary'))['salary__avg'] or 0
    dept_counts = Employee.objects.values('department').annotate(total=Count('department'))
    
    context = {
        'total_employees': total_employees,
        'avg_salary': avg_salary,
        'dept_counts': dept_counts,
    }
    return render(request, 'dashboard.html', context)

def custom_permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)

def custom_logout(request):
    logout(request)
    return redirect('login')


# ================= ฟังก์ชันหลัก 4 ระบบ (Admin Only) =================

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def attendance_view(request):
    attendances = Attendance.objects.all().order_by('-date', '-check_in')
    if request.method == 'POST':
        emp_id = request.POST.get('employee_id')
        action = request.POST.get('action')
        
        if not emp_id:
            messages.error(request, 'กรุณาเลือกชื่อพนักงานก่อนทำรายการ')
            return redirect('attendance')

        employee = get_object_or_404(Employee, id=emp_id)
        
        # 🟢 แปลงเป็นเวลาท้องถิ่น (Local Time)
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()
        now_time = now_local.time()
        
        # ค้นหาข้อมูลแบบปลอดภัย ป้องกัน Error MultipleObjectsReturned
        att = Attendance.objects.filter(employee=employee, date=today).first()
        if not att:
            att = Attendance.objects.create(employee=employee, date=today)
            
        if action in ['check_in', 'in']:
            att.check_in = now_time
            messages.success(request, f'บันทึกเวลาเข้างานของคุณ {employee.first_name} ({now_time.strftime("%H:%M")} น.) สำเร็จ')
        elif action in ['check_out', 'out']:
            att.check_out = now_time
            messages.success(request, f'บันทึกเวลาออกงานของคุณ {employee.first_name} ({now_time.strftime("%H:%M")} น.) สำเร็จ')
        att.save()
        return redirect('attendance')

    employees = Employee.objects.all()
    return render(request, 'attendance.html', {'attendances': attendances, 'employees': employees})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def approval_view(request):
    requests = EmployeeRequest.objects.all().order_by('-created_at')
    return render(request, 'approval.html', {'requests': requests})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def update_request_status(request, req_id, status):
    req_item = get_object_or_404(EmployeeRequest, id=req_id)
    if status in ['approved', 'rejected']:
        req_item.status = status
        req_item.save()
        messages.success(request, f'อัปเดตสถานะคำขอเรียบร้อยแล้ว')
    return redirect('approval')

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def payroll_view(request):
    employees = Employee.objects.all()
    payrolls = []
    now = timezone.localtime(timezone.now())
    current_month = now.month
    current_year = now.year

    for emp in employees:
        base = float(emp.salary) if emp.salary else 0.0
        ot_records = Attendance.objects.filter(
            employee=emp, 
            date__month=current_month, 
            date__year=current_year
        ).aggregate(total_ot=Sum('overtime_hours'))

        total_ot_hours = float(ot_records['total_ot'] or 0.0)
        hourly_rate = (base / 30 / 8) if base > 0 else 0.0
        ot_pay = total_ot_hours * hourly_rate * 1.5
        sso = min(base * 0.05, 750.0)
        tax = base * 0.03
        net = (base + ot_pay) - sso - tax

        # บันทึก/อัปเดตลงตาราง Payroll Model อัตโนมัติ
        Payroll.objects.update_or_create(
            employee=emp,
            month=current_month,
            year=current_year,
            defaults={
                'base_salary': base,
                'ot_pay': ot_pay,
                'social_security': sso,
                'tax': tax,
                'net_salary': net
            }
        )

        payrolls.append({
            'employee': emp,
            'base': base,
            'ot_hours': total_ot_hours,
            'ot_pay': ot_pay,
            'sso': sso,
            'tax': tax,
            'net': net
        })

    return render(request, 'payroll.html', {'payrolls': payrolls})

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def export_bank_file(request):
    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="payroll_bank_transfer.txt"'
    
    employees = Employee.objects.all()
    lines = ["ธนาคาร|เลขที่บัญชี|ชื่อ-นามสกุล|จำนวนเงินโอน"]
    for emp in employees:
        base = float(emp.salary) if emp.salary else 0.0
        net = base - min(base * 0.05, 750.0) - (base * 0.03)
        bank = emp.get_bank_name_display() if emp.bank_name else "ไม่ระบุ"
        acc = emp.bank_account or "-"
        lines.append(f"{bank}|{acc}|{emp.first_name} {emp.last_name}|{net:.2f}")

    response.write("\n".join(lines))
    return response

@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def report_view(request):
    total_employees = Employee.objects.count()
    pending_leaves = EmployeeRequest.objects.filter(request_type='leave', status='pending').count()
    approved_ot = EmployeeRequest.objects.filter(request_type='ot', status='approved').count()
    
    employees = Employee.objects.all()
    total_salary = sum([float(emp.salary) for emp in employees if emp.salary])
    total_sso = sum([min(float(emp.salary) * 0.05, 750.0) for emp in employees if emp.salary])
    total_tax = total_salary * 0.03

    context = {
        'total_employees': total_employees,
        'pending_leaves': pending_leaves,
        'approved_ot': approved_ot,
        'total_salary': total_salary,
        'total_sso': total_sso,
        'total_tax': total_tax,
    }
    return render(request, 'report.html', context)


# ================= ฟังก์ชันระบบพนักงาน (ESS) =================

@login_required
def ess_dashboard(request):
    employees = Employee.objects.all()
    recent_requests = EmployeeRequest.objects.all().order_by('-created_at')[:10]
    
    if request.method == 'POST':
        action = request.POST.get('action')
        emp_id = request.POST.get('employee_id')
        
        if not emp_id:
            messages.error(request, 'กรุณาเลือกชื่อพนักงานก่อนทำรายการ')
            return redirect('ess_dashboard')
            
        emp = get_object_or_404(Employee, id=emp_id)
        
        if action in ['check_in', 'check_out']:
            # 🟢 แปลงเป็นเวลาท้องถิ่น (Local Time)
            now_local = timezone.localtime(timezone.now())
            today = now_local.date()
            now_time = now_local.time()
            
            # ดึงหรือสร้างแถวข้อมูลของวันนี้แบบปลอดภัย
            att = Attendance.objects.filter(employee=emp, date=today).first()
            if not att:
                att = Attendance.objects.create(employee=emp, date=today)
            
            if action == 'check_in':
                att.check_in = now_time
                messages.success(request, f'บันทึกเวลาเข้างาน {now_time.strftime("%H:%M")} น. สำเร็จ')
            elif action == 'check_out':
                att.check_out = now_time
                messages.success(request, f'บันทึกเวลาออกงาน {now_time.strftime("%H:%M")} น. สำเร็จ')
            att.save()
            
        elif action == 'submit_request':
            req_type = request.POST.get('request_type')
            title = request.POST.get('title')
            amount = request.POST.get('amount') or 0
            attachment = request.FILES.get('attachment')
            
            EmployeeRequest.objects.create(
                employee=emp,
                request_type=req_type,
                title=title,
                amount=amount,
                attachment=attachment
            )
            messages.success(request, 'ส่งคำขอสำเร็จ ระบบส่งเรื่องให้ HR อนุมัติแล้ว')
            
        return redirect('ess_dashboard')

    return render(request, 'ess_dashboard.html', {
        'employees': employees, 
        'recent_requests': recent_requests
    })
    
# ================= ระบบจัดการ OT =================
@login_required
@user_passes_test(is_admin, login_url='ess_dashboard')
def ot_management(request):
    if request.method == 'POST':
        emp_id = request.POST.get('employee_id')
        ot_hours = request.POST.get('ot_hours') or 0
        ot_date = request.POST.get('ot_date') or timezone.localtime(timezone.now()).date()
        
        emp = get_object_or_404(Employee, id=emp_id)
        
        # ค้นหาแถวของวันที่ระบุ ถ้าไม่มีให้สร้างใหม่
        att = Attendance.objects.filter(employee=emp, date=ot_date).first()
        if not att:
            att = Attendance.objects.create(employee=emp, date=ot_date)
            
        current_ot = float(att.overtime_hours) if att.overtime_hours else 0.0
        att.overtime_hours = current_ot + float(ot_hours)
        att.save()
        
        messages.success(request, f'บันทึก OT จำนวน {ot_hours} ชั่วโมง ให้คุณ {emp.first_name} เรียบร้อยแล้ว!')
        return redirect('ot_management')

    employees = Employee.objects.all()   
    return render(request, 'ot_management.html', {'employees': employees})

@csrf_exempt 
def send_support_message(request):
    if request.method == 'POST':
        sender_name = request.POST.get('sender_name', '')
        contact_info = request.POST.get('contact_info', '')
        message = request.POST.get('message', '')

        emp = Employee.objects.filter(first_name__icontains=sender_name).first()
        if not emp:
            emp = Employee.objects.first()

        title_text = f"💬 [ติดต่อแอดมิน] จาก {sender_name} (ติดต่อ: {contact_info}) - {message}"
        
        EmployeeRequest.objects.create(
            employee=emp,
            request_type='other',
            title=title_text[:255],
            amount=0
        )
        messages.success(request, 'ส่งข้อความหาแอดมินเรียบร้อยแล้ว แอดมินจะดำเนินการตรวจสอบให้ค่ะ')
    return redirect('login')