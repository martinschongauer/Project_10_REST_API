
# from api.permissions import IsAdminAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework.decorators import authentication_classes

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from api.models import User, Project, Contributor, Issue, Comment
from api.serializers import ProjectSerializer, CreateProjectSerializer, ProjectDetailSerializer
from api.serializers import ContributorSerializer, IssueSerializer
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


@api_view(['GET', 'POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def projects(request):
    """
    Work with the project list
    """

    current_user = request.user

    # Get project list for the connected user (to be implemented)
    if request.method == 'GET':
        project_list = Project.objects.filter(author_user_id=current_user)
        serializer = ProjectSerializer(project_list, many=True)
        return Response(serializer.data)

    # Create a project
    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def projects_detail(request, project_id):
    """
    More actions on a particular project
    """
    # Get more infos about a particular project
    if request.method == 'GET':
        proj = Project.objects.filter(id=project_id)
        serializer = ProjectDetailSerializer(proj, many=True)
        return Response(serializer.data)

    # Update project
    elif request.method == 'PUT':
        pass

    # Delete project
    elif request.method == 'DELETE':
        pass


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def users(request, project_id):
    """
    Manipulate users related to a project
    """
    # Get user list for this project
    if request.method == 'GET':
        proj = Project.objects.get(id=project_id)
        contrib_list = Contributor.objects.filter(project_id=proj)
        serializer = ContributorSerializer(contrib_list, many=True)
        return Response(serializer.data)

    # Add user to a project
    elif request.method == 'POST':
        pass


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def users_detail(request, project_id, user_id):
    """
    Remove user from a project
    """
    # Remove user from project
    if request.method == 'DELETE':
        pass


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def issues(request, project_id):
    """
    Manage issues related to a project
    """
    # Get issues list for this project
    if request.method == 'GET':
        proj = Project.objects.get(id=project_id)
        issues_list = Issue.objects.filter(project_id=proj)
        serializer = IssueSerializer(issues_list, many=True)
        return Response(serializer.data)

    # Add an issue to a project
    elif request.method == 'POST':
        try:
            proj = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = JSONParser().parse(request)
        if 'desc' in data and 'title' in data and 'tag' in data and 'priority' in data and 'status' in data:
            Issue.objects.create(author_user_id=User.objects.get(username='admin@oc.com'),
                                 assignee_user_id=User.objects.get(username='admin@oc.com'),
                                 project_id=proj,
                                 desc=data['desc'],
                                 title=data['title'],
                                 tag=data['tag'],
                                 priority=data['priority'],
                                 status=data['status'])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def issues_detail(request, project_id, issue_id):
    """
    More actions related to a particular issue
    """
    # Update issue
    if request.method == 'PUT':
        data = JSONParser().parse(request)
        try:
            obj = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Keep current values as default before updating
        update_fields = {
            "desc": obj.desc,
            "title": obj.title,
            "tag": obj.tag,
            "priority": obj.priority,
            "status": obj.status
        }

        # Modify values found in POST payload
        if 'desc' in data:
            update_fields['desc'] = data['desc']

        if 'title' in data:
            update_fields['title'] = data['title']

        if 'tag' in data:
            update_fields['tag'] = data['tag']

        if 'priority' in data:
            update_fields['priority'] = data['priority']

        if 'status' in data:
            update_fields['status'] = data['status']

        # Updating...
        obj.desc = update_fields['desc']
        obj.title = update_fields['title']
        obj.tag = update_fields['tag']
        obj.priority = update_fields['priority']
        obj.status = update_fields['status']
        obj.save()

        return Response(status=status.HTTP_202_ACCEPTED)

    # Delete issue
    elif request.method == 'DELETE':
        try:
            obj = Issue.objects.get(id=issue_id)
            obj.delete()
            return Response(status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comments(request, project_id, issue_id):
    """
    Comments-related actions
    """

    # Get corresponding issue
    try:
        issue = Issue.objects.get(id=issue_id)
    except Issue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Check user rights as a contributor on this project
    related_project = issue.project_id
    connected_user = request.user
    try:
        contrib = Contributor.objects.get(user_id=connected_user, project_id=related_project)
        # DEBUG
        print(f"User Role: {contrib.role} - Permissions {contrib.permission}")
    except Contributor.DoesNotExist:
        return Response(status=status.HTTP_403_FORBIDDEN)

    # Retrieve list of comments related to a given problem
    if request.method == 'GET':
        comments_list = Comment.objects.filter(issue_id=issue)
        serializer = CommentSerializer(comments_list, many=True)
        return Response(serializer.data)

    # Create a comment
    elif request.method == 'POST':
        # The user is indeed a contributor to this project, but does he have Read-only rights?
        if contrib.permission == "Read":
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            # ICI: le type de code que nous souhaitons, et en dessous (commenté) celui que j'utilisais
            serializer = CreateCommentSerializer(data=request.data,
                                                 context={'author_user': connected_user, 'issue': issue})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # data = JSONParser().parse(request)
        # if 'description' in data:
        #     Comment.objects.create(author_user_id=connected_user,
        #                            issue_id=issue,
        #                            description=data['description'])
        # else:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        #
        # return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['PUT', 'DELETE', 'GET'])
@permission_classes([IsAuthenticated])
def comments_detail(request, project_id, issue_id, comment_id):
    """
    Detailed actions on a particular comment
    """

    # Get comment (and check its owner)
    try:
        comment = Comment.objects.get(id=comment_id, author_user_id=request.user)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Update comment
    if request.method == 'PUT':
        serializer = UpdateCommentSerializer(comment, data=request.data)
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


    # BACKUP

    # Update comment
    # if request.method == 'PUT':
    #     data = JSONParser().parse(request)
    #     try:
    #         obj = Comment.objects.get(id=comment_id)
    #     except Comment.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #
    #     if 'description' in data:
    #         obj.description = data['description']
    #         obj.save()
    #     else:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #
    #     return Response(status=status.HTTP_202_ACCEPTED)
    #     # HTTP_201_CREATED / HTTP_400_BAD_REQUEST