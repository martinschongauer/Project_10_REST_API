from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from api.models import Project, Contributor, Issue, Comment

UserModel = get_user_model()


class Command(BaseCommand):

    help = 'Initialize project for local development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(self.help))

        # Clean a little bit
        Project.objects.all().delete()
        Contributor.objects.all().delete()
        Issue.objects.all().delete()
        Comment.objects.all().delete()
        UserModel.objects.all().delete()

        # Add users
        admin = UserModel.objects.create_superuser(username='admin@oc.com',
                                                   first_name='Baptiste', last_name='Hornecker',
                                                   email='admin@oc.com', password='password')
        user1 = UserModel.objects.create_user(username='chucknorris@oc.com',
                                              first_name='Chuck', last_name='Norris',
                                              email='chucknorris@oc.com', password='password')
        user2 = UserModel.objects.create_user(username='paveldurov@oc.com',
                                              first_name='Pavel', last_name='Durov',
                                              email='paveldurov@oc.com', password='password')
        user3 = UserModel.objects.create_user(username='anonymous@oc.com',
                                              first_name='Ano', last_name='Nymous',
                                              email='anonymous@oc.com', password='password')

        print(f"admin id: {admin.id}")
        print(f"user1 id: {user1.id}")
        print(f"user2 id: {user2.id}")
        print(f"user3 id: {user3.id}")

        # Add some projects
        project_1 = Project.objects.create(title='Algorithmes avec Python',
                                           description='Employer des algorithmes récursifs pour optimiser des investissements',
                                           type='devops',
                                           author_user_id=admin,
                                           )

        project_2 = Project.objects.create(title='Application Web de LITReview',
                                           description='Utiliser Django pour déployer un site web de revue de livres',
                                           type='frontend',
                                           author_user_id=user1,
                                           )

        # Create the "contributors" through table
        Contributor.objects.create(user_id=admin,
                                   project_id=project_1,
                                   role='Project Manager',
                                   permission="Read-Write-Delete",
                                   )

        Contributor.objects.create(user_id=admin,
                                   project_id=project_2,
                                   role='Project Manager',
                                   permission="Read-Write-Delete",
                                   )

        Contributor.objects.create(user_id=user1,
                                   project_id=project_1,
                                   role='Developer',
                                   permission="Read-Write",
                                   )

        Contributor.objects.create(user_id=user2,
                                   project_id=project_2,
                                   role='Developer',
                                   permission="Read-Write",
                                   )

        Contributor.objects.create(user_id=user3,
                                   project_id=project_2,
                                   role='Developer',
                                   permission="Read",
                                   )

        # Add three issues
        issue_1 = Issue.objects.create(title='Investments not consistent',
                                       desc='Investments obtained with three iterations can bring worse results than those obtained with only two',
                                       tag='Bug',
                                       priority="High",
                                       status='Open',
                                       author_user_id=admin,
                                       assignee_user_id=user1,
                                       project_id=project_1,
                                       )

        issue_2 = Issue.objects.create(title='Improve CSS design',
                                       desc='Add picture and try new colors to get a more appealing interface',
                                       tag='Improvement',
                                       priority="Medium",
                                       status='Closed',
                                       author_user_id=admin,
                                       assignee_user_id=user2,
                                       project_id=project_2,
                                       )

        issue_3 = Issue.objects.create(title='New forms available',
                                       desc='Please check if you think that the new forms will be comfortable for users',
                                       tag='Info',
                                       priority="Low",
                                       status='Pending',
                                       author_user_id=user2,
                                       assignee_user_id=user3,
                                       project_id=project_2,
                                       )

        # Add comments
        Comment.objects.create(description='The problem will be solved asap',
                               author_user_id=user1,
                               issue_id=issue_1,
                               )

        Comment.objects.create(description='I have several ideas to improve the website',
                               author_user_id=user2,
                               issue_id=issue_2,
                               )

        Comment.objects.create(description='Thank you a lot, I will have a look this week-end',
                               author_user_id=user3,
                               issue_id=issue_3,
                               )

        self.stdout.write(self.style.SUCCESS("All Done !"))

