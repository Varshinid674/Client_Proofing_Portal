from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.utils import timezone

from .forms import ProjectForm, CustomUserCreationForm
from .models import Project, ProjectFile, UserProfile, AuditLog


# =====================================
# HOME PAGE
# =====================================

def home(request):
    return render(request, 'proofing/home.html')


# =====================================
# USER REGISTRATION
# =====================================

def register(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']

            UserProfile.objects.create(
                user=user,
                role=role
            )

            login(request, user)
            return redirect('dashboard')

    else:
        form = CustomUserCreationForm()

    return render(request, 'proofing/register.html', {
        'form': form
    })


# =====================================
# USER LOGIN
# =====================================

def user_login(request):

    if request.method == 'POST':
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')

    else:
        form = AuthenticationForm()

    return render(request, 'proofing/login.html', {
        'form': form
    })


# =====================================
# USER LOGOUT
# =====================================

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


# =====================================
# DASHBOARD
# =====================================

@login_required
def dashboard(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'agency'}
    )

    if profile.role == 'agency':
        projects = Project.objects.filter(
            created_by=request.user
        )
    else:
        projects = Project.objects.filter(
            client_user=request.user
        )

    project_files = ProjectFile.objects.filter(
        project__in=projects
    )

    pending_approvals = project_files.filter(
        approval_status='Pending'
    ).count()

    approved_files = project_files.filter(
        approval_status='Approved'
    ).count()

    return render(request, 'proofing/dashboard.html', {
        'total_projects': projects.count(),
        'role': profile.role,
        'pending_approvals': pending_approvals,
        'approved_files': approved_files
    })


# =====================================
# ADD NEW PROJECT
# =====================================

@login_required
def add_project(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'agency'}
    )

    if profile.role != 'agency':
        return HttpResponseForbidden(
            "Only agency users can add projects."
        )

    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()

            # Record project creation
            AuditLog.objects.create(
                project=project,
                performed_by=request.user,
                action='Project Created',
                description=f"Project '{project.title}' was created."
            )

            return redirect('my_projects')

    else:
        form = ProjectForm()

    return render(request, 'proofing/add_project.html', {
        'form': form
    })


# =====================================
# MY PROJECTS
# =====================================

@login_required
def my_projects(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'agency'}
    )

    if profile.role == 'agency':
        projects = Project.objects.filter(
            created_by=request.user
        )
    else:
        projects = Project.objects.filter(
            client_user=request.user
        )

    return render(request, 'proofing/my_projects.html', {
        'projects': projects,
        'role': profile.role
    })


# =====================================
# PROJECT DETAILS AND FILE UPLOAD
# =====================================

@login_required
def project_details(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id
    )

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'agency'}
    )

    # Check project access
    if profile.role == 'agency':
        if project.created_by != request.user:
            return HttpResponseForbidden(
                "You cannot access this project."
            )
    else:
        if project.client_user != request.user:
            return HttpResponseForbidden(
                "You cannot access this project."
            )

    # Handle file upload
    if request.method == 'POST' and profile.role == 'agency':

        uploaded_file = request.FILES.get('file')

        if uploaded_file:

            project_file = ProjectFile.objects.create(
                project=project,
                file=uploaded_file,
                uploaded_by=request.user
            )

            # Record file upload
            AuditLog.objects.create(
                project=project,
                project_file=project_file,
                performed_by=request.user,
                action='File Uploaded',
                description=f"File '{project_file.file.name}' was uploaded."
            )

            return redirect(
                'project_details',
                project_id=project.id
            )

    files = ProjectFile.objects.filter(
        project=project
    )

    return render(request, 'proofing/project_details.html', {
        'project': project,
        'files': files,
        'role': profile.role
    })


# =====================================
# CLIENT FILE REVIEW
# =====================================

@login_required
@require_POST
def review_file(request, file_id):

    project_file = get_object_or_404(
        ProjectFile,
        id=file_id
    )

    project = project_file.project

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'agency'}
    )

    if profile.role != 'client':
        return HttpResponseForbidden(
            "Only clients can review files."
        )

    if project.client_user != request.user:
        return HttpResponseForbidden(
            "You are not allowed to review this file."
        )

    action = request.POST.get('action')
    feedback = request.POST.get('client_feedback', '')

    valid_actions = [
        'Approved',
        'Changes Requested',
        'Rejected'
    ]

    if action not in valid_actions:
        return HttpResponseForbidden(
            "Invalid review action."
        )

    if action in ['Changes Requested', 'Rejected'] and not feedback.strip():
        return redirect(
            'project_details',
            project_id=project.id
        )

    # Save review details
    project_file.approval_status = action
    project_file.client_feedback = feedback
    project_file.reviewed_by = request.user
    project_file.reviewed_at = timezone.now()

    project_file.save()

    # Record client review in Audit Log
    AuditLog.objects.create(
        project=project,
        project_file=project_file,
        performed_by=request.user,
        action=action,
        description=f"File '{project_file.file.name}' was {action.lower()}."
    )

    return redirect(
        'project_details',
        project_id=project.id
    )
# =====================================
# AUDIT LOG PAGE
# =====================================

@login_required
def audit_log(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'agency'}
    )

    # Get logs based on user role
    if profile.role == 'agency':

        logs = AuditLog.objects.filter(
            project__created_by=request.user
        )

    else:

        logs = AuditLog.objects.filter(
            project__client_user=request.user
        )

    logs = logs.select_related(
        'project',
        'project_file',
        'performed_by'
    ).order_by('-created_at')

    return render(request, 'proofing/audit_log.html', {
        'logs': logs
    })