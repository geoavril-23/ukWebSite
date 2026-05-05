from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('a-propos/', views.about, name='about'),
    path('actualites/', views.actualites, name='actualites'),
    path('membres/', views.members, name='members'),
    path('ressources/', views.ressources, name='ressources'),
    path('contact/', views.contact, name='contact'),

    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/messages/', views.admin_messages, name='admin_messages'),
    path('dashboard/messages/delete/<int:pk>/', views.delete_message, name='delete_message'),
    path('dashboard/messages/complete/<int:pk>/', views.mark_completed, name='mark_completed'),
    path('dashboard/users/', views.admin_users, name='admin_users'),
    path('dashboard/users/add/', views.add_user, name='add_user'),
    path('dashboard/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('dashboard/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('dashboard/users/role/<int:user_id>/', views.change_role, name='change_role'),
    path('dashboard/trash/', views.admin_trash, name='admin_trash'),
    path('dashboard/api/pending-count/', views.get_pending_count, name='get_pending_count'),

    # Profil
    path('dashboard/profile/', views.profile_view, name='profile'),
    path('dashboard/profile/update/', views.profile_update, name='profile_update'),

    # Authentification
    path('inscription/', views.user_register, name='register'),
    path('connexion/', views.user_login, name='login'),
    path('deconnexion/', views.user_logout, name='user_logout'),

    # Dashboard Visiteur
    path('mon-espace/', views.user_dashboard, name='user_dashboard'),
]
