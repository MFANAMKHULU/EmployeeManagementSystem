from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.shortcuts import reverse
from django.http import JsonResponse, HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EmployeeSerializer
from .models import Employee
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import http.client
from .forms import EmployeeForm
import hashlib
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view



def display_homepage(request):
    # You can reuse the same logic from the `get_employee_hierarchy` view
    employees = Employee.objects.all()

    employee_dict = {emp.employeeNumber: emp for emp in employees}
    root = None

    for emp in employees:
        if emp.reportsTo:
            manager = employee_dict.get(emp.reportsTo)
            if manager:
                if not hasattr(manager, 'children'):
                    manager.children = []
                manager.children.append(emp)
        else:
            root = emp

    def build_tree(employee):
        if not employee:
            return None
        return {
            'name': f"{employee.employeeNumber} - {employee.firstName} {employee.lastName}",
            'children': [build_tree(child) for child in getattr(employee, 'children', [])]
        }

    hierarchy = build_tree(root) if root else {}

    return render(request, 'admin_homepage.html', {'employee_hierarchy': hierarchy})

def add_user(request):
    """
    Retrieve the participant details and their role.
    Add participant to their role in the system.
    """
    if request.method == 'GET':
        employees = Employee.objects.all()
        return render(request, 'user_registration.html', {'employees': employees})

    return render(request, 'user_registration.html')


@require_http_methods(["POST"])
def register_employee(request):
    """
    Register a new employee.
    Handles POST request to create a new employee entry.
    """
    try:
        data = json.loads(request.body)
        
        employeeNumber = data.get('employeeNumber')
        reportsTo_id = data.get('reportsTo')

        # Validate if the employee is reporting to themselves
        if reportsTo_id and reportsTo_id == employeeNumber:
            return JsonResponse({"error": "An employee cannot report to themselves."}, status=400)

        # Check if employee number already exists
        if Employee.objects.filter(employeeNumber=employeeNumber).exists():
            return JsonResponse({"error": "Employee number already exists."}, status=400)

        # Try creating the employee and handle errors
        try:
            new_employee = Employee.objects.create(
                employeeNumber=employeeNumber,
                firstName=data.get('firstName'),
                lastName=data.get('lastName'),
                email=data.get('email'),
                birthDate=data.get('birthDate'),
                salary=data.get('salary'),
                role=data.get('role'),
                reportsTo=reportsTo_id  # Since reportsTo is now a CharField
            )
            return JsonResponse({"message": "Employee registered successfully!"}, status=201)
        except Exception as create_error:
            return JsonResponse({"error": f"Error creating employee: {create_error}"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def check_employee_number(request):
    """
    Check if an employee number already exists.
    """
    try:
        data = json.loads(request.body)
        employee_number = data.get('employeeNumber')
        
        if Employee.objects.filter(employeeNumber=employee_number).exists():
            return JsonResponse({'exists': True})
        else:
            return JsonResponse({'exists': False})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def edit_employee(request, employeeNumber):
    """
    Edit an existing employee's details.
    """
    employee = get_object_or_404(Employee, employeeNumber=employeeNumber)

    # Fetch all employees for the datalist (excluding the current employee if needed)
    employees = Employee.objects.exclude(employeeNumber=employee.employeeNumber)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'edit_employee.html', {'form': form, 'employee': employee,})

def remove_employee(request):
    """
    Remove selected employees from the system.
    """
    if request.method == "POST":
        selected_employees = request.POST.getlist('selected_employees')

        if selected_employees:
            # Clean up the employee numbers
            selected_employees = [emp_num.strip() for emp_num in selected_employees]

            # Delete selected employees
            deleted_count, _ = Employee.objects.filter(employeeNumber__in=selected_employees).delete()

            if deleted_count:
                messages.success(request, "Employee(s) successfully removed")
            else:
                messages.error(request, "No employees found to remove")

        else:
            messages.error(request, "No employee selected")
    
        return redirect('user_list')
    
    # Handle invalid request methods
    messages.error(request, "Invalid request method")
    return redirect('user_list')

def list_users(request):
    """
    Return all employees or those matching the search query, with sorting.
    """
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'employeeNumber')
    sort_order = request.GET.get('sort_order', 'asc')

    # Fetch employees from the database using Django ORM
    employees = Employee.objects.all()

    if search_query:
        search_query = search_query.lower()
        employees = employees.filter(
            Q(firstName__icontains=search_query) |
            Q(lastName__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employeeNumber__icontains=search_query) |
            Q(role__icontains=search_query) |
            Q(salary__icontains=search_query) |
            Q(birthDate__icontains=search_query)
        )

    # Sorting employees
    if sort_order == 'desc':
        sort_by = f'-{sort_by}'
    employees = employees.order_by(sort_by)

    # Add Gravatar URL to employees
    employees = list(employees)
    for emp in employees:
        email_hash = hashlib.md5(emp.email.lower().encode('utf-8')).hexdigest()
        emp.gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s=80&d=identicon"

    # Prepare hierarchical data
    employee_dict = {emp.employeeNumber: emp for emp in employees}
    roots = []

    for emp in employees:
        if emp.reportsTo:
            manager = employee_dict.get(emp.reportsTo)
            if manager:
                if not hasattr(manager, 'children'):
                    manager.children = []
                manager.children.append(emp)
            else:
                roots.append(emp)
        else:
            roots.append(emp)

    def build_tree(employee):
        if not employee:
            return None
        return {
            'name': f"{employee.firstName} {employee.lastName}",
            'children': [build_tree(child) for child in getattr(employee, 'children', [])]
        }

    # Build hierarchy for multiple roots
    hierarchy = [build_tree(root) for root in roots]

    # Determine the next sort order for each column
    def next_sort_order(current_sort_by):
        if sort_by.lstrip('-') == current_sort_by and sort_order == 'asc':
            return 'desc'
        return 'asc'

    context = {
        'employees': employees,
        'search_query': search_query,
        'sort_by': sort_by.lstrip('-'),
        'sort_order': sort_order,
        'next_sort_order': {
            'employeeNumber': next_sort_order('employeeNumber'),
            'firstName': next_sort_order('firstName'),
            'lastName': next_sort_order('lastName'),
            'email': next_sort_order('email'),
            'birthDate': next_sort_order('birthDate'),
            'salary': next_sort_order('salary'),
            'role': next_sort_order('role'),
        },
        'employee_hierarchy': hierarchy
    }

    return render(request, 'user_list.html', context)


@api_view(['GET'])
def get_employee_hierarchy(request):
    employees = Employee.objects.all()
    employee_dict = {emp.employeeNumber: emp for emp in employees}
    root = None

    for emp in employees:
        if emp.reportsTo and emp.reportsTo != "None":
            manager = employee_dict.get(emp.reportsTo)
            if manager:
                if not hasattr(manager, 'children'):
                    manager.children = []
                manager.children.append(emp)
        else:
            root = emp

    def build_tree(employee):
        if not employee:
            return None
        return {
            'name': f"{employee.employeeNumber} - {employee.firstName} {employee.lastName}",
            'children': [build_tree(child) for child in getattr(employee, 'children', [])]
        }

    hierarchy = build_tree(root) if root else {}
    return JsonResponse(hierarchy)



@login_required(login_url='/admin/login/')
def resources(request):
    """
    Redirect to Django admin for more configuration.
    """
    admin_url = reverse('admin:index')
    return HttpResponseRedirect(admin_url)

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Employee instances.
    """
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all().order_by('-id')
