from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 🟢 บังคับให้วิ่งมาใช้ฟังก์ชันออกจากระบบที่เราสร้างเอง ป้องกัน Error 405
    path('logout/', views.custom_logout, name='logout'),
    
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='password_change.html',
        success_url='/profile/'
    ), name='password_change'),
    
    path('', views.index, name='index'),
    path('create/', views.employee_create, name='create'),
    path('detail/<int:pk>/', views.employee_detail, name='detail'),
    path('update/<int:pk>/', views.employee_update, name='update'),
    path('delete/<int:pk>/', views.employee_delete, name='delete'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('approval/', views.approval_view, name='approval'),
    path('approval/<int:req_id>/<str:status>/', views.update_request_status, name='update_request_status'),
    path('payroll/', views.payroll_view, name='payroll'),
    path('payroll/export-bank/', views.export_bank_file, name='export_bank_file'),
    path('reports/', views.report_view, name='reports'),
    path('ess/', views.ess_dashboard, name='ess_dashboard'),
    path('ot-management/', views.ot_management, name='ot_management'),
    path('send-support/', views.send_support_message, name='send_support'),
]

# สำหรับแสดงรูปภาพในโหมด Production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)