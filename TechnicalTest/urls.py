"""
URL configuration for TechnicalTest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
import main
from main import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_homepage/',views.display_homepage,name='admin_homepage'),
    path('',views.display_homepage,name='admin_homepage'),
    path('user_registration/',views.add_user,name='user_registration'),
    path('user_list/',views.list_users,name='user_list'),
    path('resources/',views.resources,name='resources'),
    path('',include('main.urls')),
    path('employee/', views.register_employee, name='register_employee'),
    path('remove_employee/', views.remove_employee, name='remove_employee'),
    path('employee/edit/<str:employeeNumber>/', views.edit_employee, name='edit_employee'),
    path('get_employee_hierarchy/', views.get_employee_hierarchy, name='get_employee_hierarchy'),
    path('check_employee_number/', views.check_employee_number, name='check_employee_number'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)