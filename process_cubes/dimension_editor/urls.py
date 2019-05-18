from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<int:pk>/dimensions', views.dimension_edit, name='dimension-edit'),
    path('<int:pk>/events', views.get_events, name="get-events"),
    path('<int:pk>/attributes', views.get_attrs, name="get-attrs"),
    path('<int:pk>/remove_dimension', views.remove_dimension, name="remove-dimension"),
    path('<int:pk>/add_dimension', views.add_dimension, name="add-dimension"),
    path('<int:pk>/free_attributes', views.get_free_attributes, name="free-attributes"),
    path('<int:pk>/add_attribute', views.add_attribute, name="add-attributes"),
    path('<int:pk>/rem_attribute', views.rem_attribute, name="rem-attribute"),
]