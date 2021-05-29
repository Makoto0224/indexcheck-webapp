from django.urls import path
from . import views


app_name = 'indexcheck'

urlpatterns = [
    path('', views.index_list, name='index_list'),
    path('detail/<int:pk>/', views.index_detail, name='index_detail'),
    path('create/', views.index_create, name='index_create'),
    path('update/<int:pk>/', views.index_update, name='index_update'),
    path('delete/<int:pk>/', views.index_delete, name='index_delete'),
    path('plot/<int:pk>/', views.get_svg, name='index_plot'),
    path('signup/', views.signup, name='signup'),
    path('hello/', views.hello, name='hello'),
    ]
