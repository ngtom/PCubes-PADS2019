from django.urls import path

from . import views

urlpatterns = [
    path('<int:cube_id>/dim/<int:dim_id>/slice', views.slice, name='dimension-edit'),
]