
import os
import json
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render


#Function to determine whether the line that extends horizontally to the
#right of point will intersect with line segment (a,b)
def on_left(point, a, b):
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
        result_states = []
        point = [longitude,latitude]

        with open(os.path.join(settings.BASE_DIR,'states.json')) as file_:
            for line in file_:
                states.append(json.loads(line))

        for state in states:
            edges = state['border']
            in_state = False

            for i in xrange(len(edges)-1):
                if on_left(point, edges[i], edges[i+1]):
                    in_state = not in_state

            if in_state:
                result_states.append(state['state'])

        return HttpResponse(str(point) + " is in state(s): " + ','.join(result_states))
    else:
        return HttpResponse("No input")
