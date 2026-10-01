from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    # กำหนด min_value=0 เพื่อให้เงินเดือนต้องไม่ติดลบ
    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )

    class Meta:
        model = Employee
        fields = '__all__' 