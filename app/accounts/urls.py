from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', view=views.index, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('docs/upload/', views.upload_document, name='upload_document'),
    path('docs/list/', views.document_list, name='document_list'),
    path('docs/verify/', views.verify_document_view, name='verify_document'),
]