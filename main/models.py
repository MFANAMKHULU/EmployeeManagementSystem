from django.db import models

class Employee(models.Model):
    employeeNumber=models.CharField(max_length=10)
    lastName=models.CharField(max_length=200)
    firstName=models.CharField(max_length=200)
    email=models.EmailField(max_length=100)
    birthDate=models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    role=models.CharField(max_length=200)
    reportsTo = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.employeeNumber
