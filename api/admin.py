from django.contrib import admin

from api.models import User, Project, Contributor, Issue, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'type')


class ContributorAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'project_id', 'role')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'desc', 'tag', 'status', 'priority')


admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Comment)

