
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from api.models import User, Project, Contributor, Issue, Comment
from api.serializers import ProjectSerializer, UpdateProjectSerializer, ProjectDetailSerializer, CreateProjectSerializer
from api.serializers import ContributorSerializer, UpdateContributorSerializer, CreateContributorSerializer
from api.serializers import IssueSerializer, UpdateIssueSerializer, CreateIssueSerializer
from api.serializers import CommentSerializer, UpdateCommentSerializer, CreateCommentSerializer

from django.shortcuts import render
from . import forms


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"SAVED : {user.username}")
    return render(request, 'api/signup.html', context={'form': form})


# -------------------------
#   Projects related code
# -------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def projects(request):
    """
    Work with the project list
    """

    connected_user = request.user

    # Get full project list
    if request.method == 'GET':
        project_list = Project.objects.all()
        serializer = ProjectSerializer(project_list, many=True)
        return Response(serializer.data)

    # Create a project
    elif request.method == 'POST':
        request.data.update({'author_user_id': connected_user.id})
        serializer = CreateProjectSerializer(data=request.data)

        if serializer.is_valid():
            proj = serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Add a single contributor from now: the creator as manager
        new_contrib = Contributor.objects.create(user_id=connected_user,
                                                 project_id=proj,
                                                 role="Project Manager",
                                                 permission="Read-Write-Delete")

        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def projects_detail(request, project_id):
    """
    More actions on a particular project
    """

    # Find project or quit immediately
    try:
        proj = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Are we contributor to this project?
    connected_user = request.user
    try:
        contrib = Contributor.objects.get(user_id=connected_user, project_id=proj)
    except Contributor.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Get detailed infos about a particular project
    if request.method == 'GET':
        serializer = ProjectDetailSerializer(proj)
        return Response(serializer.data)

    # Update project
    elif request.method == 'PUT':
        if proj.author_user_id == connected_user:
            serializer = UpdateProjectSerializer(proj, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # Delete project (available for its creator only)
    elif request.method == 'DELETE':
        if proj.author_user_id == connected_user:
            proj.delete()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # Everything OK
    return Response(status=status.HTTP_200_OK)


# ----------------------
#   Users related code
# ----------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def users(request, project_id):
    """
    Manipulate users related to a project
    """

    # Get project infos - if it exists
    try:
        proj = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Check if the connected user is a contributor - necessary for any further operation
    connected_user = request.user
    try:
        contrib = Contributor.objects.get(user_id=connected_user, project_id=proj)
    except Contributor.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Get user list for this project
    if request.method == 'GET':
        contrib_list = Contributor.objects.filter(project_id=proj)
        serializer = ContributorSerializer(contrib_list, many=True)
        return Response(serializer.data)

    # Add user to a project
    elif request.method == 'POST':
        # In order to add a new user, we have to be the project creator
        if proj.author_user_id != connected_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # The "UniqueConstraint" in contributor model protects us against if a user is added twice
        request.data.update({'project_id': project_id})
        serializer = CreateContributorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def users_detail(request, project_id, user_id):
    """
    Remove/Modify user
    """

    # Get project infos - if it exists
    try:
        proj = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Check if the connected user has enough rights on this project (= created it)
    connected_user = request.user
    if proj.author_user_id != connected_user:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Find the user we want to update/remove
    try:
        user_obj = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Find contributor entry in the table for this user
    try:
        contrib = Contributor.objects.get(user_id=user_obj, project_id=proj)
    except Contributor.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        serializer = UpdateContributorSerializer(contrib, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        contrib.delete()
        return Response(status=status.HTTP_200_OK)


# -----------------------
#   Issues related code
# -----------------------

def is_user_contributor(user_obj, project):
    """
    Check whether a user contributes to a given project
    """

    try:
        contrib = Contributor.objects.get(user_id=user_obj, project_id=project)
    except Contributor.DoesNotExist:
        return False

    # The user was found
    return True


def get_issue_infos(issue_id, connected_user):
    """
    Get contributor infos + issue
    """

    # Get corresponding issue
    try:
        issue = Issue.objects.get(id=issue_id)
    except Issue.DoesNotExist:
        raise ValueError(status.HTTP_400_BAD_REQUEST)

    # Retrieve user rights as a contributor on this project
    related_project = issue.project_id

    try:
        contrib = Contributor.objects.get(user_id=connected_user, project_id=related_project)
    except Contributor.DoesNotExist:
        raise ValueError(status.HTTP_400_BAD_REQUEST)

    return related_project, issue, contrib


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def issues(request, project_id):
    """
    Manage issues related to a project
    """

    connected_user = request.user
    try:
        proj = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Connected user needs to be a project contributor to access issues
    if not is_user_contributor(connected_user, proj):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Get issues list for this project
    if request.method == 'GET':
        proj = Project.objects.get(id=project_id)
        issues_list = Issue.objects.filter(project_id=proj)
        serializer = IssueSerializer(issues_list, many=True)
        return Response(serializer.data)

    # Add an issue to a project
    elif request.method == 'POST':
        request.data.update({'author_user_id': connected_user.id,
                            'project_id': proj.id})
        serializer = CreateIssueSerializer(data=request.data)

        # Check here if the user is not a contributor
        if serializer.is_valid():
            new_issue = serializer.save()
            if not is_user_contributor(new_issue.assignee_user_id, proj):
                new_issue.delete()
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def issues_detail(request, project_id, issue_id):
    """
    More actions related to a particular issue
    """

    connected_user = request.user
    try:
        related_project, issue, contrib = get_issue_infos(issue_id, connected_user)
    except ValueError as err:
        return Response(status=err.args)

    # Update issue - if it belongs to connected user
    if request.method == 'PUT':
        if issue.author_user_id == connected_user:
            serializer = UpdateIssueSerializer(issue, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # Delete issue if we own it and
    elif request.method == 'DELETE':
        if issue.author_user_id == connected_user:
            issue.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# -------------------------
#   Comments related code
# -------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comments(request, project_id, issue_id):
    """
    Comments-related actions
    """

    connected_user = request.user
    try:
        related_project, issue, contrib = get_issue_infos(issue_id, connected_user)
    except ValueError as err:
        return Response(status=err.args)

    # Retrieve list of comments related to a given problem
    if request.method == 'GET':
        comments_list = Comment.objects.filter(issue_id=issue)
        serializer = CommentSerializer(comments_list, many=True)
        return Response(serializer.data)

    # Create a comment
    elif request.method == 'POST':
        # Permissions could be used here, or to create an issue, but it does not necessarily correspond
        # to the requirements -> leave it commented
        # if contrib.permission == "Read":
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        # Create a new comment with default values
        request.data.update({'author_user_id': connected_user.id,
                             'issue_id': issue.id})
        serializer = CreateCommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE', 'GET'])
@permission_classes([IsAuthenticated])
def comments_detail(request, project_id, issue_id, comment_id):
    """
    Detailed actions on a particular comment
    """

    connected_user = request.user

    # Get comment (and check its owner)
    try:
        comment = Comment.objects.get(id=comment_id, author_user_id=connected_user)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Update comment
    if request.method == 'PUT':
        serializer = UpdateCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Remove comment
    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_200_OK)

    # Get comment by id
    elif request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
