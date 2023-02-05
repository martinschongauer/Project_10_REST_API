from django.contrib import admin
from django.urls import path
from api import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', views.signup_page),
    path('projects/', views.projects, name='view_projects'),
    path('projects/<int:project_id>/', views.projects_detail),
    path('projects/<int:project_id>/users/', views.users),
    path('projects/<int:project_id>/users/<int:user_id>/', views.users_detail),
    path('projects/<int:project_id>/issues/', views.issues),
    path('projects/<int:project_id>/issues/<int:issue_id>/', views.issues_detail),
    path('projects/<int:project_id>/issues/<int:issue_id>/comments/', views.comments),
    path('projects/<int:project_id>/issues/<int:issue_id>/comments/<int:comment_id>/', views.comments_detail),
]
