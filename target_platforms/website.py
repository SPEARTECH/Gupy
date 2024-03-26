from . import base
import os

class Website(base.Base):
    index_content = '''
{% load static %}

<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, minimal-ui">
  <link href="{% static 'css/output.css' %}" type="text/css" rel="stylesheet"/>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>

<body>
  
  <div id="app">[[ message ]]</div>

</body>
<script>
  const { createApp } = Vue

  createApp({
    delimiters: ["[[","]]"],
    data() {
      return {
        message: 'Welcome!'
      }
    }
  }).mount('#app')
</script>


'''
    urls_content = '''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    ]    
    '''
    
    admin_url_content = ''
    server_content = ''
    
    def __init__(self, name, lang):
        self.name = name
        self.lang = lang
        self.admin_urls_content = f'''
"""selfcert URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('',include('{self.name}_app.urls')),
    path('admin/', admin.site.urls),
]
'''
        self.folders = [f'{self.name}/website', f'{self.name}/website/dev']
        self.files = {
            f'/{self.name}_app/templates/index.html': self.index_content,
            f'{self.name}_app/urls.py': self.urls_content,
            f'{self.name}/urls.py': self.admin_urls_content,
            }
        if self.lang.lower() == 'py':
          self.server_content = f'''
from django.shortcuts import render
from {self.name}_app.models import *

# Create your views here.
def index(request):
    ''' + r'''
    context = {}
    return render(request, 'index.html', context)
    '''
#         elif self.lang.lower() == 'go':
#           self.server_content = f'''
# from django.shortcuts import render
# from {self.name}.models import *
# '''+r'''
# def index(request):
#     context = {}
#     return render(request, 'index.html, context')

#     '''

    def create(self):
        for folder in self.folders:
            os.mkdir('apps/'+folder)
            print(f'created "{folder}" folder.')
        print('starting django project...')
        os.system('echo changing directory')
        os.chdir(f'apps/{self.name}/website/dev/') #go into newly created dev folder
        # os.system('pwd')
        os.system(f'django-admin startproject {self.name}')
        print('creating django app...')
        os.chdir(self.name)
        os.system(f'python manage.py startapp {self.name}_app')
        os.mkdir(f'{self.name}_app/templates')
        os.mkdir(f'{self.name}_app/static')
        os.mkdir(f'{self.name}_app/static/css')
        # add npm install, init, tailwindcss install, init, daisyui install, tailwind config generation (with daisy theme)
        for file in self.files:
            with open(os.getcwd()+file, 'w') as f:
              f.write(self.files.get(file))
              print(f'created "{file}" file.')
        with open(f'{self.name}_app/views.py','w') as f:
          f.write(self.server_content)


