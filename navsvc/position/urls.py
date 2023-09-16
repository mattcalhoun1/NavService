from django.urls import path
from position import views

urlpatterns = [
    path('nav_maps/', views.nav_maps),
    path('nav_map/<str:map_id>/', views.nav_map),
    path('recognition_model/<str:model_id>/<str:model_type>/<str:model_format>/', views.recognition_model),
    path('vehicles/', views.vehicles),
    path('recent_sessions/<str:vehicle_id>/', views.recent_sessions),
    path('assignments/<str:vehicle_id>/', views.assignments),
    path('assignment/<str:vehicle_id>/<str:entry_num>/', views.assignment),
    path('assignment_create/<str:vehicle_id>/', views.assignment_create),
    path('position_log/<str:vehicle_id>/<str:session_id>/', views.position_log),
    path('position_log/<str:vehicle_id>/<str:session_id>/<str:start_time>/', views.position_log),
    path('position_log/<str:vehicle_id>/<str:session_id>/<str:start_time>/<str:end_time>/', views.position_log),
    path('position_views/<str:vehicle_id>/<str:session_id>/', views.position_views),
    path('position_view/<str:vehicle_id>/<str:entry_num>/<str:camera_id>/', views.position_view),
    path('lidar_entries/<str:vehicle_id>/<str:session_id>/', views.lidar_entries),
    path('lidar/<str:vehicle_id>/<str:session_id>/<str:entry_num>/', views.lidar),
    path('lidar/<str:vehicle_id>/<str:session_id>/', views.lidar),
    path('shutdown/', views.shutdown),

]
