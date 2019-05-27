from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<int:cube_id>/cells-table', views.list_cells, name='list-cells'),
    path('<int:cube_id>/cells', views.get_cells, name='get-cells'),
]