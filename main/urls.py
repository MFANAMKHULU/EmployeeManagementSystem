from django.urls import path, include
from .views import EmployeeViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'employee', EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
