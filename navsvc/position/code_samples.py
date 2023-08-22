# to be run in django shell script

# creating a new vehicle
from position.models import Vehicle
from position.serializers import VehicleSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

car = Vehicle(vehicle_id='car.1', name='elegoo_car')
car.save()

car2 = Vehicle(vehicle_id='car.2', name='elegoo_car_2')
car2.save()
