from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<int:cube_id>/dimensions', views.dimension_edit, name='dimension-edit'),
    path('<int:cube_id>/remove_dimension', views.remove_dimension, name="remove-dimension"),
    path('<int:cube_id>/add_dimension', views.add_dimension, name="add-dimension"),
    # path('<int:cube_id>/free_attributes', views.get_free_attributes, name="free-attributes"),
    path('<int:cube_id>/add_attribute', views.add_attribute, name="add-attributes"),
    path('<int:cube_id>/rem_attribute', views.rem_attribute, name="rem-attribute"),
]