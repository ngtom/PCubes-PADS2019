from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/slice', views.slice_operation, name='dimension-edit'),
    path('<int:pk>/dice', views.dice_operation, name='dimension-edit'),
]