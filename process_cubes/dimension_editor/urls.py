from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/dimensions', views.dimension_edit, name='dimension-edit'),
]