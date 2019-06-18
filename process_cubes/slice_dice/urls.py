from django.urls import path

from . import views

urlpatterns = [
    path('<int:cube_id>/dim/<int:dim_id>/slice', views.slice, name='slice'),
    path('<int:cube_id>/dim/<int:dim_id>/dice', views.dice, name='dice'),
    path('<int:cube_id>/dim/<int:dim_id>/slice/save', views.slice_save, name="slice_save")
]