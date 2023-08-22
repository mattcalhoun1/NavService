from django.urls import path
from position import views

urlpatterns = [
    path('nav_map/<str:map_id>/', views.nav_map),
    path('recognition_model/<str:model_id>/<str:model_type>/<str:model_format>/', views.recognition_model),
    path('position_log/<str:vehicle_id>/<str:session_id>/', views.position_log),
    path('position_log/<str:vehicle_id>/<str:session_id>/<str:start_time>/', views.position_log),
    path('position_log/<str:vehicle_id>/<str:session_id>/<str:start_time>/<str:end_time>/', views.position_log),
]