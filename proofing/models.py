from django.db import models
from django.contrib.auth.models import User


# =========================================
# 1. USER ROLE MANAGEMENT
# =========================================

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('agency', 'Agency'),
        ('client', 'Client'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='agency'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# =========================================
# 2. PROJECT MANAGEMENT
# =========================================

class Project(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    client_name = models.CharField(
        max_length=100
    )

    client_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_projects'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


# =========================================
# 3. PROJECT FILES AND APPROVAL MANAGEMENT
# =========================================

class ProjectFile(models.Model):

    APPROVAL_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Changes Requested', 'Changes Requested'),
        ('Rejected', 'Rejected'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='files'
    )

    file = models.FileField(
        upload_to='project_files/'
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    approval_status = models.CharField(
        max_length=30,
        choices=APPROVAL_CHOICES,
        default='Pending'
    )

    client_feedback = models.TextField(
        blank=True
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_files'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.file.name


# =========================================
# 4. AUDIT LOG MANAGEMENT
# =========================================

class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('Project Created', 'Project Created'),
        ('File Uploaded', 'File Uploaded'),
        ('Approved', 'Approved'),
        ('Changes Requested', 'Changes Requested'),
        ('Rejected', 'Rejected'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )

    project_file = models.ForeignKey(
        ProjectFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.action} - {self.project.title}"