from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('products/', views.product_list, name='product_list'),
    path(
        'products/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),
    path(
        'products/<int:product_id>/movement/',
        views.create_movement,
        name='create_movement'
    ),

    path('suppliers/', views.supplier_list, name='supplier_list'),
    path(
        'suppliers/<int:supplier_id>/',
        views.supplier_detail,
        name='supplier_detail'
    ),

    path('categories/', views.category_list, name='category_list'),

    path(
        'categories/<int:category_id>/',
        views.category_detail,
        name='category_detail'
    ),

    path(
        'movements/',
        views.movement_charts,
        name='movement_charts'
    ),
]