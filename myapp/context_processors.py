from .models import Employee

def get_employee_data(request):
    if request.user.is_authenticated:
        emp = Employee.objects.filter(
            first_name=request.user.first_name, 
            last_name=request.user.last_name
        ).first()
        return {'current_emp': emp}
    return {}