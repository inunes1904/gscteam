from django.urls import path

from projects.views import create_project
from . import views

urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('register/', views.register_user, name="register"),

    path('', views.profiles, name='profiles'),
    path('profile/<str:pk>', views.profile, name="profile"),
    path('account/', views.account, name="account"),
    path('profile_form/', views.edit_account, name='edit_account'),
    
    path('skill_form/', views.create_skill, name='create_skill'),
    path('update_skill/<str:pk>', views.update_skill, name='update_skill'),
    path('delete_skill/<str:pk>', views.delete_skill, name="delete_skill"),

    path('inbox/', views.inbox, name="inbox"),
    path('message/<str:pk>', views.view_message, name="message"),
    path('create_message/<str:pk>', views.create_message, name="create_message"),
]
