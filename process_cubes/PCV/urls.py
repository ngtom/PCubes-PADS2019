from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/dimensions', views.createPCV, name='PCV-edit'),
]