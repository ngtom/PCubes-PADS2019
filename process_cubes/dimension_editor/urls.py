from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<int:cube_id>/dimensions', views.dimension_edit, name='dimension-edit'),
    path('<int:cube_id>/remove_dimension', views.remove_dimension, name="remove-dimension"),
    path('<int:cube_id>/add_dimension', views.add_dimension, name="add-dimension"),
    path('<int:cube_id>/add_attribute', views.add_attribute, name="add-attributes"),
    path('<int:cube_id>/rem_attribute', views.rem_attribute, name="rem-attribute"),
    path('<int:cube_id>/save_dim_name', views.save_dim_name, name="save-dim-name"),
]