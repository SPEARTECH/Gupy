from . import base
import os

class Website(base.Base):
    index_content = '''<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/vuesax/dist/vuesax.css" rel="stylesheet">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, minimal-ui">
</head>
<body>
  <div id="app">
    <vs-button vs-type="filled">Welcome to Raptor!</vs-button>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vuesax/dist/vuesax.umd.js"></script>
  <script>
    new Vue({
        el: '#app'
    })
  </script>
</body>
</html> '''

    server_content = ''

    def __init__(self, name, lang):
        self.name = name
        self.lang = lang
        self.folders = [f'{self.name}/website', f'{self.name}/website/dev']
        self.files = {
            f'/{self.name}_app/templates/index.html': self.index_content,
            }
        if self.lang.lower() == 'py':
          self.server_content = f'''
from django.shortcuts import render
from {self.name}.models import *
'''+r'''
def index(request):
    context = {}
    return render(request, 'index.html, context')

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
            os.mkdir(folder)
            print(f'created "{folder}" folder.')
        print('starting django project...')
        os.system('echo changing directory')
        os.chdir(f'{self.name}/website/dev/') #go into newly created dev folder
        # os.system('pwd')
        os.system(f'django-admin startproject {self.name}')
        print('creating django app...')
        os.chdir(self.name)
        os.system(f'python manage.py startapp {self.name}_app')
        os.system(f'mkdir {self.name}_app/templates')
        for file in self.files:
            with open(os.getcwd()+file, 'w') as f:
              f.write(self.files.get(file))
              print(f'created "{file}" file.')
        with open(f'{self.name}_app/views.py','a+') as f:
          f.write(self.server_content)


