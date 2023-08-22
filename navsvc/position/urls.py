from django.urls import path
from position import views

urlpatterns = [
    path('vehicles/', views.vehicle_list),
    path('vehicle/<int:pk>/', views.vehicle_detail),
    path('position_log/<str:vehicle_id>/', views.position_log),
    path('position_log/<str:vehicle_id>/<str:start_time>/', views.position_log),
    path('position_log/<str:vehicle_id>/<str:start_time>/<str:end_time>/', views.position_log),

]