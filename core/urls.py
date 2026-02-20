from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('research/', views.research_index, name='research_index'),
    path('research/catalog/', views.research_catalog, name='research_catalog'),
    path('public/', views.public_index, name='public_index'),
    path('public/dashboard/', views.public_dashboard, name='public_dashboard'),
    # AI API
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/interpret/compound/', views.api_interpret_compound, name='api_interpret_compound'),
    path('api/interpret/dashboard/', views.api_interpret_dashboard, name='api_interpret_dashboard'),
]
