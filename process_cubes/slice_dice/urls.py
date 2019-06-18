from django.urls import path

from . import views

urlpatterns = [
    path('<int:cube_id>/slice/<int:dim_id>/', views.slice_operation, name='slice'),
    path('<int:cube_id>/slice/<int:dim_id>/save_slice', views.save_slice, name='save-slice'),
    path('<int:cube_id>/dice/<int:dim_id>/save_dice', views.save_dice, name='save-dice'),
    path('<int:cube_id>/dice/<int:dim_id>/', views.dice_operation, name='dice'),
]