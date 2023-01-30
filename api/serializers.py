from rest_framework import serializers

from api.models import User, Project, Contributor, Issue, Comment


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'author_user_id', 'id']


class CreateProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'author_user_id']


class UpdateProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['title', 'description', 'type']


class ProjectDetailSerializer(serializers.ModelSerializer):

    project_issues = serializers.SerializerMethodField()
    contributors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'author_user_id', 'project_issues', 'contributors']

    def get_project_issues(self, instance):
        queryset = instance.project_issue.all()
        serializer = IssueSummarySerializer(queryset, many=True)
        return serializer.data

    def get_contributors(self, instance):
        queryset = instance.project_contributor.all()
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data


class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['title', 'desc', 'tag', 'priority', 'status', 'author_user_id',
                  'assignee_user_id', 'project_id', 'created_time', 'id']


class CreateIssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['title', 'desc', 'tag', 'priority', 'status', 'assignee_user_id', 'author_user_id', 'project_id']


class UpdateIssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['title', 'desc', 'tag', 'priority', 'status']


class IssueSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['title', 'created_time', 'id']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'id']


class UserSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'id']


class ContributorSerializer(serializers.ModelSerializer):

    contributor_user = serializers.SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ['role', 'permission', 'contributor_user']

    def get_contributor_user(self, instance):
        # queryset = instance.user_id.all()
        serializer = UserSummarySerializer(instance.user_id)
        return serializer.data


class CreateContributorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contributor
        fields = ['permission', 'role', 'user_id', 'project_id']


class UpdateContributorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contributor
        fields = ['permission', 'role']


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['description', 'author_user_id', 'issue_id', 'created_time', 'id']


class CreateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['description', 'author_user_id', 'issue_id']


class UpdateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['description']

