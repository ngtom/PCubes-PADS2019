from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/pcv', views.createPCV, name='PCV-edit'),
]
