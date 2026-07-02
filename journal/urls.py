from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_setup, name='add_setup'),
    path('log/', views.setup_list, name='setup_list'),
    path('setup/<int:pk>/', views.setup_detail, name='setup_detail'),
    path('setup/<int:pk>/delete/', views.setup_delete, name='setup_delete'),
    path('analytics/', views.analytics, name='analytics'),
    path('mastery/', views.mastery, name='mastery'),
    path('finding/<int:pk>/delete/', views.finding_delete, name='finding_delete'),
    path('strategy/', views.strategy_page, name='strategy_page'),
]
