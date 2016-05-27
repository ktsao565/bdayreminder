from django.shortcuts import render
#longitude is x, latitude is y
# Create your views here.
import os
import requests, json
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings


def on_left(point,a,b):
    if (point[1] < min(b[1],a[1])) or (point[1] > max(b[1],a[1])):
        return False
    slope = (b[1]-a[1])/(b[0]-a[0])
    y_intercept = b[1]-slope*b[0]
    x_line = (point[1] - y_intercept)/slope
    if point[0] <= x_line:
        return True
    return False


def index(request):
    return render(request,'findstate/index.html')

def results(request):
    if 'latitude' in request.GET and 'longitude' in request.GET:
        latitude = float(request.GET['latitude'])
        longitude = float(request.GET['longitude'])
        states = []
        results = []
        point = [longitude,latitude]
        with open(os.path.join(settings.BASE_DIR,'states.json')) as file_:
            for line in file_:
                states.append(json.loads(line))
        for state in states:
            result = state['border']
            in_state = False
            for i in xrange(len(result)-1):
                if on_left(point,result[i],result[i+1]):
                    in_state = not in_state
            if in_state:
                results.append(state['state'])
        return HttpResponse("States: " + ''.join(results) + str(point))
    else:
        return HttpResponse("No input")
