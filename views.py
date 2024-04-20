
from django.shortcuts import render
from gupyceo_app.models import *

# Create your views here.
def index(request):
    
    context = {}
    return render(request, 'index.html', context)
    