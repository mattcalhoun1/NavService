from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from position.models import Vehicle, PositionLog, PositionLogEntry, NavMap
from position.serializers import VehicleSerializer, PositionLogEntrySerializer
import logging
from datetime import datetime

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
    
@csrf_exempt
def vehicle_detail(request, pk):
    """
    Retrieve, update or delete a vehicle
    """
    try:
        vehicle = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = VehicleSerializer(vehicle)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = VehicleSerializer(vehicle, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        vehicle.delete()
        return HttpResponse(status=204)