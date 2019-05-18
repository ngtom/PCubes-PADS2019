from django.urls import path
from . import views

urlpatterns = [
    path('<int:cube_id>/pcv', views.createPCV, name='PCV-edit'),
]
