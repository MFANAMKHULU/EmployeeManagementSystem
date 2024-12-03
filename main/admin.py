from django.contrib import admin
from .models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employeeNumber', 'lastName', 'firstName', 'email', 'birthDate', 'salary', 'role', 'reportsTo']
admin.site.register(Employee,EmployeeAdmin)