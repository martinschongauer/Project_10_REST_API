from django.urls import reverse_lazy

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

from api.models import Project, Contributor, Issue, Comment, User


class TestCategory(APITestCase):
    # Store URLs for all the endpoints
    url_login = reverse_lazy('token_obtain_pair')
    url_view_projects = reverse_lazy('view_projects')

    def create_user(self):
        """Creates a sample user for the tests

        return values: a user object + login/pass
        """
        email = 'user@test.com'
        password = 'userpass1'
        username = 'user'

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.save()

        return user, username, password

    def create_project(self, user):
        """Creates a typical project for the tests

        param user: the project author (a user)
        return value: a project object
        """
        proj = Project.objects.create(title="Test.py project",
                                      description="This project was created by tests.py",
                                      type="devops",
                                      author_user_id=user)

        return proj

    def log_jwt(self, username, password):
        """Retrieve token for bearer - required everywhere
        """

        resp = self.client.post(self.url_login,
                                {'username': username, 'password': password},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_projects_get(self):
        # Let's create a user for this test, and his first project
        user, username, password = self.Create_User()
        proj = self.Create_Project(user)

        # Log in
        self.log_jwt(username, password)

        # Read project list
        response = self.client.get(self.url_view_projects)
        self.assertEqual(response.status_code, 200)
        excepted = [
            {
                'title': "Test.py project",
                'description': "This project was created by tests.py",
                'type': "devops",
                'author_user_id': 1,
                'id': proj.id,
            }
        ]
        self.assertEqual(excepted, response.json())

    def test_projects_post_put_del(self):
        # Create a user and log in
        user, username, password = self.Create_User()
        self.log_jwt(username, password)

        # The project is, this time, created thanks to a POST
        response = self.client.post(self.url_view_projects,
                                    {'title': "Test.py project",
                                     'description': "Project created with test.py",
                                     'type': "backend",
                                     'author_user_id': user.id},
                                     format='json')
        self.assertEqual(response.status_code, 201)

        # Check newly created project
        response = self.client.get(self.url_view_projects)
        self.assertEqual(response.status_code, 200)
        excepted = [
            {
                'title': "Test.py project",
                'description': "Project created with test.py",
                'type': "backend",
                'author_user_id': user.id,
                'id': 1,
            }
        ]
        self.assertEqual(excepted, response.json())

        # For later calls, URL to manipulate this project
        url_project = self.url_view_projects + "1/"

        # Modify project fields - test PUT
        response = self.client.put(url_project,
                                   {'title': "Test.py project - MODIFIED", 'type': "devops"},
                                   format='json')
        self.assertEqual(response.status_code, 202)

        # Check modifications
        response = self.client.get(self.url_view_projects)
        self.assertEqual(response.status_code, 200)
        excepted = [
            {
                'title': "Test.py project - MODIFIED",
                'description': "Project created with test.py",
                'type': "devops",
                'author_user_id': user.id,
                'id': 1,
            }
        ]
        self.assertEqual(excepted, response.json())

        # Try some invalid value
        response = self.client.put(url_project,
                                   {'type': "invalid"},
                                   format='json')
        self.assertEqual(response.status_code, 400)

        # Delete project
        response = self.client.delete(url_project)
        self.assertEqual(response.status_code, 200)
