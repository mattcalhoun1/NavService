from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from position.models import Lidar,Vehicle, PositionLog, PositionLogEntry, NavMap, NavModel, PositionView, Assignment
from position.serializers import LidarSerializer,AssignmentSerializer, VehicleSerializer, PositionLogEntrySerializer, PositionViewSerializer, NavigationMapSerializer, NavigationModelSerializer
import logging
from datetime import datetime

@csrf_exempt
def nav_maps(request):
    logging.getLogger(__name__).info(f"maps {request.method}")

    """
    Get a all active maps
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving maps")
        serializer = NavigationMapSerializer(data=None)
        nav_maps = serializer.get_maps()
        serializer.cleanup()
        out_serializer = NavigationMapSerializer(data=nav_maps, many=True)
        out_serializer.is_valid()
        return JsonResponse(out_serializer.data, safe=False)
    
    return JsonResponse({}, safe=False)

@csrf_exempt
def nav_map(request, map_id):
    logging.getLogger(__name__).info(f"map {request.method}: {map_id}")

    """
    Get a specific map
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving map: {map_id}")
        #vehicles = Vehicle.objects.all()
        serializer = NavigationMapSerializer(data=None)
        nav_map = serializer.get_map(map_id)
        serializer.cleanup()
        out_serializer = NavigationMapSerializer(data=nav_map)
        out_serializer.is_valid()
        if nav_map is not None:
            return JsonResponse(nav_map.content, safe=False)
    
    return JsonResponse({}, safe=False)

@csrf_exempt
def recognition_model(request, model_id, model_type, model_format):
    logging.getLogger(__name__).info(f"recognition_model {request.method}: {model_id}, {model_type}, {model_format}")

    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving model: {model_id}")
        #vehicles = Vehicle.objects.all()
        serializer = NavigationModelSerializer(data=None)
        nav_model = serializer.get_model (model_id, model_type, model_format)
        serializer.cleanup()
        out_serializer = NavigationModelSerializer(data=nav_model)
        out_serializer.is_valid()
        return JsonResponse({
            "model_type": nav_model.model_type,
            'model_format': nav_model.model_format,
            'additional_params': nav_model.additional_params,
            "encoded_model": nav_model.encoded_model,
        }, safe=False)

@csrf_exempt
def position_views(request, vehicle_id, session_id):
    logging.getLogger(__name__).info(f"position_views {request.method}: {vehicle_id}, {session_id}")

    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Searching for position views")
        serializer = PositionViewSerializer(data=None)
        pos_views = serializer.get_all_matching(vehicle_id=vehicle_id, session_id=session_id)
        serializer.cleanup()
        out_serializer = PositionViewSerializer(data=pos_views, many=True)
        out_serializer.is_valid()
        return JsonResponse(out_serializer.data, safe=False)
    
@csrf_exempt
def position_view(request, vehicle_id, entry_num = None, camera_id = None):
    logging.getLogger(__name__).info(f"position_view {request.method}: {vehicle_id}, {entry_num}, {camera_id}")

    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving image")
        #vehicles = Vehicle.objects.all()
        serializer = PositionViewSerializer(data=None)
        pos_view = serializer.get_position_image(vehicle_id=vehicle_id, entry_num=entry_num, camera_id=camera_id)
        serializer.cleanup()
        return JsonResponse({
            "image_format": 'png',
            'vehicle_id':vehicle_id,
            'entry_num': entry_num,
            'camera_id':camera_id,
            'encoded_image': pos_view
        }, safe=False)
    elif request.method == 'POST':
        logging.getLogger(__name__).info(f"Saving image")
        data = JSONParser().parse(request)
        #vehicles = Vehicle.objects.all()
        serializer = PositionViewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer.cleanup()
            return JsonResponse({'result':'success'}, status=201)

@csrf_exempt
def lidar_entries(request, vehicle_id, session_id):
    logging.getLogger(__name__).info(f"position_views {request.method}: {vehicle_id}, {session_id}")
    """
    List all lidar entries for the given session.
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Searching for lidar entries")
        serializer = LidarSerializer(data=None)
        lidar_views = serializer.get_all_matching(vehicle_id=vehicle_id, session_id=session_id)
        serializer.cleanup()
        out_serializer = LidarSerializer(data=lidar_views, many=True)
        out_serializer.is_valid()
        return JsonResponse(out_serializer.data, safe=False)
    
@csrf_exempt
def lidar(request, vehicle_id, session_id, entry_num = None):
    logging.getLogger(__name__).info(f"lidar {request.method}: {vehicle_id}, {entry_num}")

    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving lidar")
        #vehicles = Vehicle.objects.all()
        serializer = LidarSerializer(data=None)
        lidar_entry = serializer.get_lidar_data(vehicle_id=vehicle_id, entry_num=entry_num)
        serializer.cleanup()
        return JsonResponse({
            'session_id':lidar_entry.session_id,
            'vehicle_id':lidar_entry.vehicle_id,
            'occurred':lidar_entry.occurred,
            'lidar_data':lidar_entry.lidar_data
        }, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        logging.getLogger(__name__).info(f"Saving lidar: {data}")
        serializer = LidarSerializer(data=data)
        if serializer.is_valid():
            logging.getLogger(__name__).info("data is valid")
            serializer.save()
            serializer.cleanup()
            return JsonResponse({'result':'success'}, status=201)

@csrf_exempt
def recent_sessions(request, vehicle_id):
    logging.getLogger(__name__).info(f"recent_sessions {request.method}: {request}")

    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving recent sessions, vehicle: {vehicle_id}")
        #vehicles = Vehicle.objects.all()
        serializer = PositionLogEntrySerializer(data=None)
        entries = serializer.get_recent_sessions (vehicle_id = vehicle_id, max_sessions = 10)
        serializer.cleanup()
        return JsonResponse(entries, safe=False)

@csrf_exempt
def position_log(request, vehicle_id, session_id, start_time = None, end_time = None):
    logging.getLogger(__name__).info(f"position_log {request.method}: {request}")

    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving position log, vehicle: {vehicle_id}, session: {session_id}, start time: {start_time}, end time: {end_time}")
        #vehicles = Vehicle.objects.all()
        serializer = PositionLogEntrySerializer(data=None)
        entries = serializer.get_all_matching(vehicle_id=vehicle_id, session_id=session_id, start_time=start_time, end_time=end_time)
        serializer.cleanup()
        out_serializer = PositionLogEntrySerializer(data=entries, many=True)
        out_serializer.is_valid()
        return JsonResponse(out_serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PositionLogEntrySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer.cleanup()
            return JsonResponse(serializer.data, status=201)

        serializer.cleanup()
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def vehicles(request):
    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        #vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(None)
        vehicles = serializer.get_all_vehicles()
        serializer.cleanup()
        return JsonResponse(vehicles, safe=False)

@csrf_exempt
def assignments(request, vehicle_id):
    logging.getLogger(__name__).info(f"assignments {request.method}: {request}")

    """
    Get assignments or update one
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving assignments, vehicle: {vehicle_id}")
        serializer = AssignmentSerializer(data=None)
        entries = serializer.get_incomplete(vehicle_id=vehicle_id)
        serializer.cleanup()
        out_serializer = AssignmentSerializer(data=entries, many=True)
        out_serializer.is_valid()
        return JsonResponse(out_serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PositionLogEntrySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer.cleanup()
            return JsonResponse(serializer.data, status=201)

        serializer.cleanup()
        return JsonResponse(serializer.errors, status=400)
    
@csrf_exempt
def assignment(request, vehicle_id, entry_num):
    logging.getLogger(__name__).info(f"assignment {request.method}: {request}")

    """
    Get assignments or update one
    """
    if request.method == 'GET':
        logging.getLogger(__name__).info(f"Retrieving assignment, vehicle: {vehicle_id}, entry: {entry_num}")
        serializer = AssignmentSerializer(data=None)
        assn = serializer.get(vehicle_id=vehicle_id, entry_num=int(entry_num))
        serializer.cleanup()
        out_serializer = AssignmentSerializer(data=assn)
        out_serializer.is_valid()
        return JsonResponse(out_serializer.data, safe=False)

    elif request.method == 'POST':
        logging.getLogger(__name__).info(f"{request.body}")
        data = JSONParser().parse(request)
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer.cleanup()
            return JsonResponse(serializer.data, status=200)

        serializer.cleanup()
        return JsonResponse(serializer.errors, status=400)
    
@csrf_exempt
def assignment_create(request, vehicle_id):
    logging.getLogger(__name__).info(f"assignment create {request.method}: {request}")

    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer.cleanup()
            return JsonResponse(serializer.data, status=201)

        serializer.cleanup()
        return JsonResponse(serializer.errors, status=400)
