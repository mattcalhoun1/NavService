from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from position.models import Vehicle, PositionLog, PositionLogEntry, NavMap, NavModel
from position.serializers import VehicleSerializer, PositionLogEntrySerializer, NavigationMapSerializer, NavigationModelSerializer
import logging
from datetime import datetime

@csrf_exempt
def nav_map(request, map_id):
    logging.getLogger(__name__).info(f"map {request.method}: {map_id}")

    """
    List all vehicles, or create a new vehicle.
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
def vehicle_list(request):
    """
    List all vehicles, or create a new vehicle.
    """
    if request.method == 'GET':
        #vehicles = Vehicle.objects.all()
        vehicles = []
        for i in range(10):
            vehicles.append(Vehicle(vehicle_id=f"v{i}", name="another vehicle"))

        serializer = VehicleSerializer(vehicles, many=True)
        serializer.cleanup()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = VehicleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer.cleanup()
            return JsonResponse(serializer.data, status=201)

        serializer.cleanup()
        return JsonResponse(serializer.errors, status=400)
    
