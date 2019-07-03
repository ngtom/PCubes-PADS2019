from django.urls import path

from . import views

urlpatterns = [
    path('upload', views.upload, name='upload'),    
    path('<int:log_id>/events', views.get_events, name="get-events"),
    path('<int:log_id>/attributes', views.get_attrs, name="get-attrs"),
    path('<int:log_id>/attr/<int:attr_id>/values', views.get_attr_values, name="get-attr-values"),
]