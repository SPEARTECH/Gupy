from . import base
import os
import platform
import glob

class Website(base.Base):
    index_content = '''
<!DOCTYPE html>

{% load static %}


 <!-- Documentation:
   https://daisyui.com/
   https://tailwindcss.com/
   https://www.highcharts.com/
   https://vuejs.org/
   https://pyodide.org/en/stable/
   https://www.papaparse.com/
   https://danfo.jsdata.org/
   https://axios-http.com/docs/intro -->

<html>
<head>
  <title>Gupy App</title>
  <script src="https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js"></script>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.7.2/dist/full.min.css" rel="stylesheet" type="text/css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/danfojs@1.1.2/lib/bundle.min.js"></script>
  <script src="https://code.highcharts.com/highcharts.js"></script>
  <script src="https://code.highcharts.com/modules/boost.js"></script>
  <script src="https://code.highcharts.com/modules/exporting.js"></script>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, minimal-ui">
  <link rel="icon" href="./gupy_logo.png" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle h-96 hover:-translate-y-2 ease-in-out transition" src="./gupy_logo.png" />
        <br>
        <button class="btn bg-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/50 text-base-100">[[ message ]] </button>
      </div>
    </center>
  </div>
</body>
<script>
  // Disable right-clicking
document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});
</script>
  <script>
    const { createApp } = Vue
    
    createApp({
      delimiters : ['[[', ']]'],
        data(){
          return {
            message: 'Welcome to Gupy!',
            data: {},
          }
        },
        methods: {

        },
        watch: {

        },
        created(){
            // Make a request for a user with a given ID
            axios.get('/api/example_api_endpoint')
            .then(function (response) {
                // handle success
                console.log(response);
                this.data = JSON.parse(JSON.stringify(response['data']))
                console.log(this.data)
            })
            .catch(function (error) {
                // handle error
                console.log(error);

            // use pyodide instead of api example
        async function main(
          pyodide_msg,
        ){
          const pyodide = await loadPyodide();
          pyodide.registerJsModule("mymodule", { 
            pyodide_msg:pyodide_msg,
        })
        await pyodide.loadPackage("numpy")
        await pyodide.runPython(`
from mymodule import *

pyodide_msg = 'This is the changed pyodide message!'

response = {'new_msg':pyodide_msg}
`)
      main(this.pyodide_msg).then(response => {
        response = JSON.parse(response['new_msg'])
        console.log(response)
                
            })
            .finally(function () {
                // always executed
            });
          }
        })
      },
        mounted() {

        },
        computed:{

        }

    }).mount('#app')
  </script>
</html>      
'''

    urls_content = '''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    ]    
    '''
    
    server_content = ''

    python_modules_content = '''
import os
from ctypes import cdll, c_char_p

def main():
    path = os.path.dirname(os.path.realpath(__file__))

    # Load the shared library
    try:
        go_modules = cdll.LoadLibrary(path+'/../go_modules/go_modules.so')
    except Exception as e:
        print(str(e)+'\\n Try running `python ./gupy.py gopherize -t <target_platform> -n <app_name>`')
        return

    # Define the return type of the function
    go_modules.go_module.restype = c_char_p

    # Call the Go function and decode the returned bytes to a string
    result = go_modules.go_module().decode('utf-8')

    return result

if __name__ == "__main__":
    main() 


    '''


    go_modules_content = '''
package main

import (
    "C"
)

//export go_module
func go_module() *C.char {
    response := "Welcome to Gupy!"

    return C.CString(response)
}

func main() {
    // c_module()
}    
    '''



    def __init__(self, name):
        self.name = name
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
        self.folders = [f'{self.name}/website']
        self.files = {
            f'/{self.name}_app/templates/index.html': self.index_content,
            f'/{self.name}_app/urls.py': self.urls_content,
            f'/{self.name}/urls.py': self.admin_urls_content,
            }
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
      system = platform.system()

      if system == 'Darwin':
          cmd = 'python3'
      elif system == 'Linux':
          cmd = 'python'
      else:
          cmd = 'python'

      for folder in self.folders:
          os.mkdir('apps/'+folder)
          print(f'created "{folder}" folder.')
      print('starting django project...')
      os.system('echo changing directory...')
      os.chdir(f'apps/{self.name}/website/') #go into newly created folder
      # os.system('pwd')
      try:
        os.system(f'django-admin startproject {self.name}')
      except Exception as e:
        print(str(e)+'\nFailure to run django-admin; try installing django with `python -m pip install django`')
        return
      print('creating django app...')
      # print(os.getcwd())
      os.chdir(self.name)
      os.system(f'{cmd} manage.py startapp {self.name}_app')
      os.mkdir(f'{self.name}_app/templates')
      os.mkdir(f'{self.name}_app/python_modules')
      f = open(f'{self.name}_app/python_modules/python_modules.py', 'x')
      f.write(self.python_modules_content)
      print(f'created "{self.name}_app/python_modules/python_modules.py" file.')
      f.close()
      os.mkdir(f'{self.name}_app/go_modules')
      f = open(f'{self.name}_app/go_modules/go_modules.go', 'x')
      f.write(self.go_modules_content)
      print(f'created "{self.name}_app/go_modules/go_modules.go" file.')
      f.close()    
      os.chdir(f'{self.name}_app/go_modules/')
      os.system(f'go mod init example/go_modules')
      os.chdir('../')
      os.mkdir(f'static')
      os.system(f'cp ')
      os.mkdir(f'static/css')
      os.chdir('../')
      # add npm install, init, tailwindcss install, init, daisyui install, tailwind config generation (with daisy theme)
      for file in self.files:
          with open(os.getcwd()+file, 'w') as f:
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
      with open(f'views.py','w') as f:
        f.write(self.server_content)

    # def compile(self,name):
    #   pass

    def cythonize(self,name):
        if os.path.exists(f"apps/{name}/website/{self.name}_app/python_modules"):
            os.chdir(f'apps/{name}/website/{self.name}_app/python_modules')
            # files = [f for f in os.listdir('.') if os.path.isfile(f)]
            setup_content = '''
from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
            '''
            # for f in files:
            #     os.system(f'cp{f} {f}x')
            files = [f for f in glob.glob('*.py')]
            if 'setup.py' in files:
                files.remove('setup.py')
            for file in files:
                with open(file, 'r') as f:
                    py_content = ''
                    for item in f.readlines():
                        py_content = py_content + item
                if os.path.exists(file+'x'):
                    f = open(f'{file}x', 'r+')
                    f.seek(0)
                    f.truncate()
                    f.close()
                else:
                    f = open(f'{file}x', 'x')
                f = open(f'{file}x', 'r+')
                f.write(py_content)
                print(f'Updated {file}x file.')
                f.close()

                setup_content = setup_content + f'"{file}x",\n'
            setup_content = setup_content + '''     ])
    )
            '''
            if os.path.exists('setup.py'):
                f = open('setup.py', 'r+')
                f.seek(0)
                f.truncate()
                f.close()
            else:
                f = open('setup.py', 'x')
            f = open('setup.py', 'r+')
            f.write(setup_content)
            print(f'Updated setup.py file.')
            f.close()
            os.system(f'python ./setup.py build_ext --inplace')

    def gopherize(self,name):
        if os.path.exists(f"apps/{name}/website/{self.name}_app/go_modules"):
            os.chdir(f'apps/{name}/website/{self.name}_app/go_modules')
            os.system(f'go mod tidy')
            files = [f for f in glob.glob('*.go')]
            for file in files:
                print(f'Building {file} file...')
                os.system(f'go build -o {os.path.splitext(file)[0]}.so -buildmode=c-shared {file} ')