from django.shortcuts import render

# Create your views here.
import requests, json
from django.http import HttpResponse, HttpResponseRedirect


def index(request):
    return HttpResponse("Hello")
