from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employeeNumber', 'firstName', 'lastName', 'email', 'birthDate', 'salary', 'role', 'reportsTo']

