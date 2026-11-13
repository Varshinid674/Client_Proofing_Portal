from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('register/', views.register, name='register'),

    path('login/', views.user_login, name='login'),

    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('add-project/', views.add_project, name='add_project'),

    path('my-projects/', views.my_projects, name='my_projects'),

    path(
        'project/<int:project_id>/',
        views.project_details,
        name='project_details'
    ),

    path(
        'review-file/<int:file_id>/',
        views.review_file,
        name='review_file'
    ),

    path(
        'audit-log/',
        views.audit_log,
        name='audit_log'
    ),

]