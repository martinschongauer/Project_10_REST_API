from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

# null = False -> can't be created without this field
# CASCADE -> delete element if one of these users disappear
# related_name for the inverse relation


class User(AbstractUser):
    pass
    # username = None
    # email = models.EmailField(_('email address'), unique=True)
    #
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []


class Project(models.Model):

    TYPES = (
        ("frontend", "frontend"),
        ("backend", "backend"),
        ("devops", "devops"),
        ("management", "management"),
    )

    title = models.fields.CharField(max_length=128, null=False)
    description = models.fields.CharField(max_length=2048, blank=True, null=False)
    type = models.fields.CharField(max_length=50, null=False, choices=TYPES)
    author_user_id = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE,
                                       related_name='author_user_project')

    def __str__(self):
        return self.title
    # Not used here
    # class Meta:
    #     unique_together = ("user", "followed_user")


class Contributor(models.Model):
    # user_id = models.PositiveIntegerField()
    # project_id = models.PositiveIntegerField()

    ROLES = (
        ("Project Manager", "Project Manager"),
        ("Developer", "Developer"),
    )

    PERMISSIONS = (
        ("Read", "Read"),
        ("Read-Write", "Read-Write"),
        ("Read-Write-Delete", "Read-Write-Delete"),
    )

    user_id = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE,
                                related_name='user_contributor')
    project_id = models.ForeignKey(to=Project, null=False, on_delete=models.CASCADE,
                                   related_name='project_contributor')
    role = models.fields.CharField(max_length=128, null=False, choices=ROLES)
    permission = models.fields.CharField(max_length=40, null=False, choices=PERMISSIONS)

    def __str__(self):
        return self.role


class Issue(models.Model):

    TAG = (
        ("Bug", "Bug"),
        ("Feature", "Feature"),
        ("Improvement", "Improvement"),
        ("Info", "Info"),
    )

    PRIORITY = (
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    )

    STATUS = (
        ("Open", "Open"),
        ("Closed", "Closed"),
        ("Pending", "Pending"),
    )

    title = models.fields.CharField(max_length=128, null=False)
    desc = models.fields.CharField(max_length=128, null=False)
    tag = models.fields.CharField(max_length=128, null=False, choices=TAG)
    priority = models.fields.CharField(max_length=20, null=False, choices=PRIORITY)
    status = models.fields.CharField(max_length=20, null=False, choices=STATUS)
    author_user_id = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE,
                                       related_name='author_user_issue')
    assignee_user_id = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE,
                                         related_name='assignee_user_issue')
    # project_id = models.PositiveIntegerField()
    project_id = models.ForeignKey(to=Project, null=False, on_delete=models.CASCADE,
                                   related_name='project_issue')
    created_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    description = models.fields.CharField(max_length=128, null=False)
    author_user_id = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE,
                                       related_name='author_user_comment')
    issue_id = models.ForeignKey(to=Issue, null=False, on_delete=models.CASCADE,
                                 related_name='issue_comment')
    created_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

