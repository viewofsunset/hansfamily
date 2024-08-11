from django.shortcuts import render, redirect, reverse 
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q





def index(request):
    return HttpResponse("Hello world. this is hans endtertainment root page")