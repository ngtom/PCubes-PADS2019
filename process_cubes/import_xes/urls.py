from django.urls import path

from . import views

urlpatterns = [
    path('upload', views.upload, name='upload'),    
    path('<int:log_id>/events', views.get_events, name="get-events"),
    path('<int:log_id>/attributes', views.get_attrs, name="get-attrs"),
]