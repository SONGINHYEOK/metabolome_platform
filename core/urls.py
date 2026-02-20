from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('research/', views.research_index, name='research_index'),
    path('research/catalog/', views.research_catalog, name='research_catalog'),
    path('public/', views.public_index, name='public_index'),
    path('public/dashboard/', views.public_dashboard, name='public_dashboard'),
]
