from . import base
import os
import platform
import glob
import re
import subprocess
import shutil
import sys
from colorama import Fore, Style
import click

def ensure_wasm_exec(dest_dir: str = ".") -> bool:
    """
    Copy wasm_exec.js from the local Go toolchain into dest_dir.
    If not found, prompt user to install/reinstall Go and return False.
    """
    dest_dir = os.path.abspath(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "wasm_exec.js")

    try:
        goroot = subprocess.run(
            ["go", "env", "GOROOT"], check=True, capture_output=True, text=True
        ).stdout.strip()
    except Exception:
        print("Go toolchain not found on PATH. Please install/reinstall the latest Go from https://go.dev/dl and try again.")
        return False

    candidates = [
        os.path.join(goroot, "misc", "wasm", "wasm_exec.js"),  # standard path
        os.path.join(goroot, "lib", "wasm", "wasm_exec.js"),   # some distro layouts
    ]
    for src in candidates:
        if os.path.isfile(src):
            shutil.copyfile(src, dest)
            print(f"Copied wasm_exec.js from: {src}")
            return True

    print("wasm_exec.js not found under your GOROOT.")
    print(f"Tried: {candidates}")
    print("Please install/reinstall the latest Go from https://go.dev/dl, then re-run.")
    return False


class Website(base.Base):

    index_content = '''

<!DOCTYPE html>
{% load static %}
<!-- Documentation links... -->
<html data-theme="light">
<head>
  <title>Gupy App</title>
  <script src="https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js"></script>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <link href="https://cdn.jsdelivr.net/npm/daisyui@5/themes.css" rel="stylesheet" type="text/css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/danfojs@1.1.2/lib/bundle.min.js"></script>
  <script src="https://code.highcharts.com/highcharts.js"></script>
  <script src="https://code.highcharts.com/modules/boost.js"></script>
  <script src="https://code.highcharts.com/modules/exporting.js"></script>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, minimal-ui">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  <link rel="icon" href="{% static 'logo/gupy_logo.png' %}" type="image/png">
  <script src="{% static 'go_wasm/wasm_exec.js' %}"></script>
</head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle  h-96 w-96 max-h-full max-w-full object-contain hover:-translate-y-2 ease-in-out transition" src="{% static 'logo/gupy_logo.png' %}" />
        <br>
        <br>
        <button class="btn bg-blue-500 border-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-md hover:shadow-blue-500/50 text-base-100 shadow-none transition-shadow ">[[ message ]] </button>
        <br>
        <br>
        <!-- This block only appears on https apps for installing as a PWA standalone on your device -->
        <div v-if="pwa_install" role="alert" class="alert shadow-lg">
            <!--<div role="alert" class="alert shadow-lg">-->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            class="stroke-info shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>Install this app on your device!</span>
            <div>
            <button
                class=" btn btn-sm bg-blue-500  text-white  shadow-sm  hover:bg-blue-500/50 shadow-blue-500/50 hover:shadow-md hover:shadow-blue-500/50 hover:-translate-y-0.5 no-animation"
                @Click="prompt" id="install">Install</button>
            </div>
            
        </div>
        <br>

      </div>
    </center>
  </div>
</body> 
<!-- <script>
  // Disable right-clicking
document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});
</script> -->
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js', { scope: '/' });
  }
</script>
  <script type="module">
    const { createApp } = Vue
     import { loadGoWasm } from '{% static "go_wasm.js" %}';    
    createApp({
      delimiters : ['[[', ']]'],
        data(){
          return {
            message: 'Welcome to Gupy!',
            pyodide_msg: 'This is from Pyodide!',
            data: {},
            pwa_install: '',
          }
        },
        methods: {
            prompt() {
                this.pwa_install.prompt()
            },
        },
        watch: {

        },
        created(){
              // This variable will save the event for later use.
                window.addEventListener('beforeinstallprompt', (e) => {
                    // Prevents the default mini-infobar or install dialog from appearing on mobile
                    //   e.preventDefault();
                    // Save the event because you'll need to trigger it later.
                    this.pwa_install = e;
                    // Show your customized install prompt for your PWA
                    // Your own UI doesn't have to be a single element, you
                    // can have buttons in different locations, or wait to prompt
                    // as part of a critical journey.
                    showInAppInstallPromotion();
                });

            // Make a request for a user with a given ID
            axios.get('http://127.0.0.1:8000/example_api_endpoint')
            .then((response) => {
                // handle success
                console.log(response);
                this.data = response.data.result;
                console.log(this.data)
            })
            .catch((error) => {
                // handle error
                console.log(error);

          try {
            // use pyodide instead of api example
            async function main(){
              const pyodide = await loadPyodide();
              pyodide.registerJsModule("mymodule", {
                pyodide_msg: this.pyodide_msg,
              })
              await pyodide.loadPackage("numpy")
              const result = await pyodide.runPython(`
#import variables
import mymodule

# use variable
pyodide_msg = mymodule.pyodide_msg

# change variable
pyodide_msg = 'This is the changed pyodide message!'

# output response
response = {'new_msg':pyodide_msg}
`)
              return JSON.parse(response)
          }
            response = main()
            console.log(response.new_msg)
          } catch (error) {
            console.log('An error occurred: ', error);
          }

        })
        .finally(function () {
          // always executed
        });

      },
        async mounted() {
          try {
            const goExports = await loadGoWasm();
            console.log("add type:", typeof goExports.add);
            console.log("Go WASM add(5,7): " + goExports.add(5, 7));
          } catch (error) {
            console.error("Error loading Go WASM:", error);
          }


          let worker = new Worker("{% static 'worker.js' %}");
          worker.postMessage({ message: '' });
          worker.onmessage = function (message) {
            console.log(message.data)
          }
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
    path('example_api_endpoint/', views.example_api_endpoint, name='example_api_endpoint'),
    ]    
    '''
    
    python_modules_content = '''
import os

def main():
    result = 'Welcome to Gupy!'

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

    worker_content = '''
onmessage = function(message){
    message.data['message'] = 'This is from the worker!'

    // console.log(message.data)

    postMessage(message.data)
}  

    '''

    go_wasm_content = r'''
package main

import (
    "fmt"
    "syscall/js"
)

var addFunc js.Func // avoid GC

func add(this js.Value, args []js.Value) any {
    a := args[0].Int()
    b := args[1].Int()
    sum := a + b
    fmt.Printf("Adding %d and %d to get %d\n", a, b, sum)
    return sum
}

func main() {
    fmt.Println("Go WebAssembly loaded and exposing functions.")
    // ADD EXPORTED FUNCTIONS HERE
    js.Global().Set("add", js.FuncOf(add))


    js.Global().Set("__go_ready__", true) // tell JS we are ready
    select {}
}
        '''




    def add_entry_to_list(self, settings_path, list_name, new_entries):
        with open(settings_path, 'r') as file:
            lines = file.readlines()

        in_list = False
        list_start = -1
        list_end = -1
        current_list = []

        for i, line in enumerate(lines):
            if line.strip().startswith(f'{list_name} = ['):
                in_list = True
                list_start = i
                current_list.append(line)
            elif in_list:
                current_list.append(line)
                if ']' in line:
                    list_end = i
                    in_list = False
                    break

        if list_start != -1 and list_end != -1:
            list_content = ''.join(current_list)
            list_items = re.findall(r'\'([^\']*)\'', list_content)
            for entry in new_entries:
                if entry not in list_items:
                    list_items.append(entry)

            new_list = f'{list_name} = [\n'
            for item in list_items:
                new_list += f"    '{item}',\n"
            new_list += ']\n'

            lines[list_start:list_end+1] = [new_list]

            with open(settings_path, 'w') as file:
                file.writelines(lines)

    def add_new_setting(self, settings_path, setting_name, setting_value):
        setting_str = f'\n# newly added\n{setting_name} = {setting_value}\n'
        with open(settings_path, 'a') as file:
            file.write(setting_str)

    def create_secret_key_file(self, secret_key_path, secret_key_value):
        with open(secret_key_path, 'w') as file:
            file.write(f"def django_secret_key():\n")
            file.write(f"    return r'{secret_key_value}'\n")

    def extract_and_replace_secret_key(self, settings_path):
        with open(settings_path, 'r') as file:
            lines = file.readlines()

        secret_key_value = None

        # Extract SECRET_KEY and replace with the function call
        for i, line in enumerate(lines):
            if line.strip().startswith('SECRET_KEY'):
                secret_key_value = re.search(r"SECRET_KEY\s*=\s*['\"](.+?)['\"]", line).group(1)
                lines[i] = "SECRET_KEY = django_secret_key()\n"
                break

        # Add import statement if not already present
        import_statement = 'from secret_key import django_secret_key'
        import_exists = any(import_statement in line for line in lines)
        if not import_exists:
            lines.insert(0, f'{import_statement}\n')

        # Write the changes back to the settings.py file
        with open(settings_path, 'w') as file:
            file.writelines(lines)

        return secret_key_value

    def __init__(self, name, lang='go'):
        self.name = name
        self.lang = lang
        self.admin_urls_content = f'''
"""{self.name} URL Configuration

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
    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.authtoken')),
]
'''
        self.views_content = f'''
from django.shortcuts import render
from {self.name}_app.models import *
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

#restframework
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import os

# Create your views here.
def index(request):
'''+r'''
    context = {}
    return render(request, 'index.html', context)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def example_api_endpoint(request):
'''+f'''
    # Get the data from the request
    # data = request.json.get('data') # for POST requests with data

    #read from python/cython module
    from {self.name}_app.python_modules import python_modules

    py_message = python_modules.main()
    
    #read from go module
    from ctypes import cdll, c_char_p

    path = os.path.dirname(os.path.realpath(__file__))

    # Load the shared library
    try:
        go_modules = cdll.LoadLibrary(path+'/go_modules/go_modules.so')
    except Exception as e:
        print(str(e)+'\\n Try running `python ./gupy.py gopherize -t <target_platform> -n <app_name>`')
        return

    # Define the return type of the function
    go_modules.go_module.restype = c_char_p
    
    go_message = go_modules.go_module().decode('utf-8')
'''+r'''
    data = {'Python Module Message':py_message,'Go Module Message':go_message}

    # Perform data processing

    response = {'result':data}

    return JsonResponse(response, safe=False)


'''
        self.manifest_content = '''
{
    "lang": "en-us",
    "name": "'''+self.name+'''",
    "short_name": "'''+self.name+''' App",
    "description": "'''+self.name+''' App",
    "start_url": "/",
    "background_color": "#2f3d58",
    "theme_color": "#2f3d58",
    "orientation": "any",
    "display": "standalone",
    "icons": [
        {
            "src": "gupy_logo.png",
            "type": "image/png",
            "sizes": "512x512"
        }
    ]
}
'''
        self.sw_content = f'''
const CACHE_NAME = `{self.name}`;
'''+r'''
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    cache.addAll([
      '/',
    ]);
  })());
});

self.addEventListener('fetch', event => {
  if (event.request.method === 'POST' || event.request.method === 'GET') {
    const modifiedRequest = event.request.clone();

    // Extract CSRF token from the DOM
    const csrfToken = getCSRFTokenFromDOM();

    // Add CSRF token to headers
    modifiedRequest.headers.append('X-CSRFToken', csrfToken);

    return fetch(modifiedRequest);
  } else {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      const cachedResponse = await cache.match(event.request);

      if (cachedResponse) {
        return cachedResponse;
      } else {
        try {
          const fetchResponse = await fetch(event.request);
          cache.put(event.request, fetchResponse.clone());
          return fetchResponse;
        } catch (e) {
          // Handle network failure
        }
      }
    })());
  }
});

function getCSRFTokenFromDOM() {
  // Implement a function to extract the CSRF token from the DOM
  // For example, if the CSRF token is in a meta tag:
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag) {
    return metaTag.content;
  } else {
    return '';
  }
}

'''
        self.go_wasm_js_content = '''
// go_wasm.js
export async function loadGoWasm() {
  if (typeof Go !== "function") throw new Error("Go runtime not found (wasm_exec.js)");
  const go = new Go();

  const url = "/static/go_wasm/go_wasm.wasm";
  const resp = await fetch(url, { cache: "no-store" });
  if (!resp.ok) throw new Error(`fetch ${url} ${resp.status}`);
  let inst;
  try {
    const r = await WebAssembly.instantiateStreaming(resp, go.importObject);
    inst = r.instance;
  } catch {
    const bytes = await resp.arrayBuffer();
    inst = (await WebAssembly.instantiate(bytes, go.importObject)).instance;
  }

  const runP = go.run(inst);
  runP.catch(e => console.error("go.run failed:", e));

  const deadline = Date.now() + 8000;
  while (!globalThis.__go_ready__) {
    if (Date.now() > deadline) throw new Error("WASM init timeout: not registered");
    await new Promise(r => setTimeout(r, 25));
  }
  return { 
    // ADD EXPORTED FUNCTIONS HERE
    add: (a, b) => globalThis.add(a, b) 

  };
}

'''

        if self.lang == 'py':
          self.folders = [
            f'website',
            ]
          self.files = {
              f'website/{self.name}/{self.name}_app/templates/index.html': self.index_content,
              f'website/{self.name}/{self.name}_app/urls.py': self.urls_content,
              f'website/{self.name}/{self.name}_app/views.py': self.views_content,
              f'website/{self.name}/{self.name}/urls.py': self.admin_urls_content,
              f'website/{self.name}/{self.name}_app/static/manifest.json': self.manifest_content,
              f'website/{self.name}/sw.js': self.sw_content,
              f'website/{self.name}/{self.name}_app/static/worker.js': self.worker_content,
              f'website/{self.name}/{self.name}_app/static/go_wasm.js': self.go_wasm_js_content,
              f'website/{self.name}/{self.name}_app/static/go_wasm/go_wasm.go': self.go_wasm_content,
              }
        else:
            self.views_content = r'''
package main

import (
	"fmt"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	r := gin.Default()

	// Enable CORS Middleware
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000", "http://127.0.0.1:5500"}, // Allow frontend domains
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		AllowCredentials: true, // Allows sending cookies & auth headers
		MaxAge:           12 * time.Hour, // Cache preflight requests for 12 hours
	}))

	// Load HTML templates
	r.LoadHTMLGlob("templates/*")

	// Serve static files
	r.Static("/static", "./static")

	// Routes
	r.GET("/", index)
	r.GET("/api/example_api_endpoint", exampleApiEndpoint) // Example API route

	// Start the server
	fmt.Println("Gupy server running at http://127.0.0.1:8080")
	if err := r.Run(":8080"); err != nil {
		fmt.Println("Server stopped:", err)
	}

	// Gracefully handle shutdown signals
	waitForShutdown()
}

// Serves an HTML template with dynamic data
func index(c *gin.Context) {
	c.HTML(http.StatusOK, "index.html", gin.H{
		"title":          "Welcome to Gupy!",
		"go_wasm_js":      "/static/go_wasm.js",
		"worker_script":  "/static/worker.js",
		"go_wasm_binary": "/static/go_wasm/go_wasm.wasm",
	})
}

// Example API route for a JSON response
func exampleApiEndpoint(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"result": "success",
	})
}

// Gracefully shuts down the server when receiving a termination signal
func waitForShutdown() {
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop // Wait for SIGINT (Ctrl+C) or SIGTERM
	fmt.Println("\nShutting down server gracefully...")
}


'''
            self.index_content = r'''

 <!-- Documentation:
   https://daisyui.com/
   https://tailwindcss.com/
   https://www.highcharts.com/
   https://vuejs.org/
   https://pyodide.org/en/stable/
   https://www.papaparse.com/
   https://danfo.jsdata.org/
   https://axios-http.com/docs/intro -->

<!DOCTYPE html>
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
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  <link rel="icon" href="/static/gupy_logo.png" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle  h-96 w-96 max-h-full max-w-full object-contain hover:-translate-y-2 ease-in-out transition" src="/static/gupy_logo.png" />
        <br>
        <button class="btn bg-blue-500 border-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-md hover:shadow-blue-500/50 text-base-100 shadow-none transition-shadow ">[[ message ]] </button>
      </div>
    </center>
</body>
<!-- <script>
  // Disable right-clicking
document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});
</script> -->
  <script type="module">
    const { createApp } = Vue
     import { loadGoWasm } from '{{ .go_wasm_js }}';
    
    createApp({
      delimiters : ['[[', ']]'],
        data(){
          return {
            message: 'Welcome to Gupy!',
            pyodide_msg: 'This is from Pyodide!',
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

          try {
            // use pyodide instead of api example
            async function main(){
              const pyodide = await loadPyodide();
              pyodide.registerJsModule("mymodule", {
                pyodide_msg: this.pyodide_msg,
              })
              await pyodide.loadPackage("numpy")
              const result = await pyodide.runPython(`
#import variables
import mymodule

# use variable
pyodide_msg = mymodule.pyodide_msg

# change variable
pyodide_msg = 'This is the changed pyodide message!'

# output response
response = {'new_msg':pyodide_msg}
`)
              return JSON.parse(response)
          }
            response = main()
            console.log(response.new_msg)
          } catch (error) {
            console.log('An error occurred: ', error);
          }

        })
        .finally(function () {
          // always executed
        });

      },
        async mounted() {
          try {
            const goExports = await loadGoWasm();
            console.log("Go WebAssembly ran add(5,7) and returned:" + goExports.add(5, 7));
          } catch (error) {
            console.error("Error loading Go WASM:", error);
          }

          let worker = new Worker("{{ .worker_script }}");
          worker.postMessage({ message: '' });
          worker.onmessage = function (message) {
            console.log(message.data)
          }

        },
        computed:{

        }

    }).mount('#app')
  </script>
</html>      
  
   
  

'''
            self.files = {
              f'website/templates/index.html': self.index_content,
              f'website/sw.js': self.sw_content,
              f'website/static/worker.js': self.worker_content,
              f'website/static/go_wasm.js': self.go_wasm_js_content,
              f'website/static/go_wasm/go_wasm.go': self.go_wasm_content,
              f'website/main.go': self.views_content,
            }
            if self.lang == 'py':
              self.folders = [
                f'website',
                f'website/{self.name}/{self.name}_app/static/go_wasm',
                f'website/{self.name}/{self.name}_app/static/logo',
                f'website/{self.name}/{self.name}_app/static/splashscreen',
                f'website/{self.name}/{self.name}_app/static/icon',
                ]
            else:
              self.folders = [
                f'website',
                f'website/templates',
                f'website/static',
                f'website/static/go_wasm',
                f'website/static/logo',
                f'website/static/splashscreen',
                f'website/static/icon',
                ]

    def create(self):
      # detect os and make folder
      system = platform.system()

      if system == 'Darwin' or system == 'Linux':
          delim = '/'
      else:
          delim = '\\'
      import shutil
      cmd = sys.executable.split(delim)[-1]

      # check if platform project already exists, if so, prompt the user
      if self.folders[0] in os.listdir('.'):
          while True:
              userselection = input(self.folders[0]+' already exists for the app '+ self.name +'. Would you like to overwrite the existing '+ self.folders[0]+' project? (y/n): ')
              if userselection.lower() == 'y':
                  click.echo(f'{Fore.YELLOW}Are you sure you want to recreate the '+ self.folders[0]+' project for '+ self.name +f'? (y/n){Style.RESET_ALL}')
                  userselection = input()
                  if userselection.lower() == 'y':
                      print("Removing old version of project...")
                      shutil.rmtree(os.path.join(os.getcwd(), self.folders[0]))
                      print("Continuing app platform creation.")
                      break
                  elif userselection.lower() != 'n':
                      click.echo(f'{Fore.RED}Invalid input, please type y or n then press enter...{Style.RESET_ALL}')
                      continue
                  else:
                      click.echo(f'{Fore.RED}Aborting app platform creation.{Style.RESET_ALL}')
                      return
              elif userselection.lower() != 'n':
                  click.echo(f'{Fore.RED}Invalid input, please type y or n then press enter...{Style.RESET_ALL}')
                  continue
              else:
                  click.echo(f'{Fore.RED}Aborting app platform creation.{Style.RESET_ALL}')
                  return
      # Get the directory of the current script
      current_directory = os.path.dirname(os.path.abspath(__file__))
      logo_directory = os.path.join(os.path.dirname(current_directory), 'gupy_logo.png') 
      splashscreen_directory = os.path.join(os.path.dirname(current_directory), 'gupy_splashscreen.png')   
      ico_directory = os.path.join(os.path.dirname(current_directory), 'gupy.ico')       

      if self.lang == 'py':
          for folder in self.folders:
              os.mkdir(folder)
              print(f'created "{folder}" folder.')
          print('starting django project...')
          os.system('echo changing directory...')
          os.chdir(f'website/') #go into newly created folder
          # os.system('pwd')
          try:
            os.system(f'django-admin startproject {self.name}')
          except Exception as e:
            click.echo(str(e)+f'\n{Fore.RED}Failure to run django-admin; try installing django with `python -m pip install django`{Style.RESET_ALL}')
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
          import shutil
          os.mkdir(f'static/css')
          os.mkdir(f'static/logo')
          os.mkdir(f'static/splashscreen')
          os.mkdir(f'static/icon')
          os.chdir('../../../')

          # # Construct the path to the target file
          # requirements_directory = os.path.join(os.path.dirname(current_directory), 'requirements.txt')       
          with open(f'website/{self.name}/requirements.txt', 'w') as f:
              f.write('''
asgiref==3.9.1
certifi==2025.8.3
cffi==1.17.1
charset-normalizer==3.4.3
cryptography==45.0.6
defusedxml==0.7.1
Django==5.2.5
django-cors-headers==4.7.0
djangorestframework==3.16.1
djangorestframework_simplejwt==5.5.1
djoser==2.3.3
idna==3.10
oauthlib==3.3.1
pillow==11.3.0
pycparser==2.22
PyJWT==2.10.1
python3-openid==3.2.0
requests==2.32.5
requests-oauthlib==2.0.0
social-auth-app-django==5.5.1
social-auth-core==4.7.0
sqlparse==0.5.3
tzdata==2025.2
urllib3==2.5.0

''')
          # shutil.copy(requirements_directory, f'website/requirements.txt')
          shutil.copy(logo_directory, f'website/{self.name}/{self.name}_app/static/logo/gupy_logo.png')
          shutil.copy(splashscreen_directory, f'website/{self.name}/{self.name}_app/static/splashscreen/gupy_splashscreen.png')
          shutil.copy(ico_directory, f'website/{self.name}/{self.name}_app/static/icon/gupy.ico')

          # add npm install, init, tailwindcss install, init, daisyui install, tailwind config generation (with daisy theme)
          os.mkdir(f'website/{self.name}/{self.name}_app/static/go_wasm')
          for file in self.files:
              with open(file, 'w') as f:
                f.write(self.files.get(file))
                print(f'created "{file}" file.')
        #   with open(f'views.py','w') as f:
        #     f.write(self.server_content)
          os.chdir(f'website/{self.name}/{self.name}_app/static/go_wasm/')
          os.system(f'go mod init example/go_wasm')
          os.chdir('../../../')
          os.chdir(f'{self.name}/')
        #   print(os.getcwd())
          settings_file_path = f'settings.py'  
          print(settings_file_path)
          # Add to lists
          self.add_entry_to_list(settings_file_path, 'ALLOWED_HOSTS', ['127.0.0.1'])
          self.add_entry_to_list(settings_file_path, 'INSTALLED_APPS', [
              'corsheaders', #newly added
              'rest_framework', #newly added
              'rest_framework.authtoken', #newly added
          ])
          self.add_entry_to_list(settings_file_path, 'MIDDLEWARE', [
              'corsheaders.middleware.CorsMiddleware', #newly added
          ])  
          # Add new setting
          self.add_new_setting(settings_file_path, 'CORS_ALLOWED_ORIGINS', [
              "http://127.0.0.1:8001",
          ])
          self.add_new_setting(settings_file_path, 'INSTALLED_APPS', [
            # Application definition
            f'{self.name}_app',
            'corsheaders', #newly added
            'rest_framework', #newly added
            'rest_framework.authtoken', #newly added
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
          ])

          os.chdir(f'../')
          secret_key_file_path = 'secret_key.py'
          # Extract the SECRET_KEY and replace it in settings.py
          secret_key_value = self.extract_and_replace_secret_key(f'{self.name}/{settings_file_path}')
          # Create the secret_key.py file with the extracted SECRET_KEY value

          self.create_secret_key_file(secret_key_file_path, secret_key_value)
          os.chdir(f'../../')
          # print(os.getcwd())
          self.cythonize()
          self.gopherize()
          self.assemble()
      else:
          for folder in self.folders:
              os.mkdir(folder)
              print(f'created "{folder}" folder.')
          for file in self.files:
              with open(file, 'w') as f:
                f.write(self.files.get(file))
                print(f'created "{file}" file.')
          with open('website/requirements.txt', 'w') as f:
              f.write('''
certifi==2025.8.3
charset-normalizer==3.4.3
idna==3.10
pillow==11.3.0
requests==2.32.4
screeninfo==0.8.1
urllib3==2.5.0
websockets==15.0.1
                        ''')

          shutil.copy(logo_directory, f'website/static/gupy_logo.png')
          shutil.copy(splashscreen_directory, f'website/static/splashscreen/gupy_splashscreen.png')
          shutil.copy(ico_directory, f'website/static/icon/gupy.ico')
          os.chdir(f'website/static/go_wasm/')
          os.system(f'go mod init example/go_wasm')
          os.chdir('../../')
          os.system(f'go mod init {self.name}')
          os.system('go get github.com/gin-contrib/cors') # do the same for gin?
          os.chdir('../')
          self.assemble()

    def run(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'

      
        if os.path.exists(f'{self.name}/manage.py'):
            # assign current python executable to use
            cmd = sys.executable.split(delim)[-1]
            os.system(f'{cmd} -m pip install -r {self.name}/requirements.txt')
            os.system(f'{cmd} {self.name}/manage.py runserver')
        else:
            os.system(f'go mod tidy')
            os.system(f'go run main.go')


    # def compile(self,name):
    #   pass

    def cythonize(self):
        # print(os.getcwd())

        if os.path.exists(f"website/{self.name}/{self.name}_app/python_modules"):
            os.chdir(f'website/{self.name}/{self.name}_app/python_modules')
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
            os.chdir('../../../../')
            print(os.getcwd())

    def gopherize(self):
        # print(os.getcwd())
        if os.path.exists(f"website/{self.name}/{self.name}_app/go_modules"):
            os.chdir(f'website/{self.name}/{self.name}_app/go_modules')
            print('Running go.mod tidy...')
            os.system(f'go mod tidy')
            files = [f for f in glob.glob('*.go')]
            for file in files:
                print(f'Building {file} file...')
                os.system(f'go build -o {os.path.splitext(file)[0]}.so -buildmode=c-shared {file} ')
            os.chdir('../../../../')
        # print(os.getcwd())

    def assemble(self):
        # print(os.getcwd())
        # print(self.lang)
        # print('printed lang/\\')
        if os.path.exists(f"website/{self.name}/{self.name}_app/static/go_wasm"):
            ensure_wasm_exec(dest_dir=os.path.join("website", f"{self.name}", f"{self.name}_app", "static", "go_wasm"))    
            os.chdir(f'website/{self.name}/{self.name}_app/static/go_wasm')
            os.system(f'go mod tidy')

            def build_wasm(filename):
              # Set the environment variables
              env = os.environ.copy()
              env['GOOS'] = 'js'
              env['GOARCH'] = 'wasm'
              
              # Command to execute
              command = f'go build -o {os.path.splitext(filename)[0]}.wasm'
              
              # Execute the command
              result = subprocess.run(command, shell=True, env=env)
              
              # Check if the command was successful
              if result.returncode == 0:
                  click.echo(f"{Fore.GREEN}Build successful.{Style.RESET_ALL}")
              else:
                  click.echo(f"{Fore.RED}Build failed.{Style.RESET_ALL}")
            files = [f for f in glob.glob('*.go')]
            for filename in files:
              build_wasm(filename)
            os.chdir('../../../../../')
        else:
            os.chdir(f'website/static/go_wasm')
            os.system(f'go mod tidy')
            ensure_wasm_exec(dest_dir=os.path.join("api", "static", "go_wasm"))    
            
            def build_wasm(filename):
              # Set the environment variables
              env = os.environ.copy()
              env['GOOS'] = 'js'
              env['GOARCH'] = 'wasm'
              
              # Command to execute
              command = f'go build -o {os.path.splitext(filename)[0]}.wasm'
              
              # Execute the command
              result = subprocess.run(command, shell=True, env=env)
              
              # Check if the command was successful
              if result.returncode == 0:
                  click.echo(f"{Fore.GREEN}Build successful.{Style.RESET_ALL}")
              else:
                  click.echo(f"{Fore.RED}Build failed.{Style.RESET_ALL}")
            files = [f for f in glob.glob('*.go')]
            for filename in files:
              build_wasm(filename)
            os.chdir('../../../')
        # add assembly of cython modules

    def distribute(self, system, folder, delim, NAME, VERSION):
        try:
            os.chdir(NAME)
            # creating project folder if doesnt already exist
            os.makedirs('dist', exist_ok=True)
            os.chdir('dist')
            if os.path.exists(f"{NAME}_{VERSION}"):
                prompt = input(f'"{NAME}_{VERSION}" folder already exists. Would you like to overwrite it? (y/n): ')
                if prompt.lower() == 'y':
                    shutil.rmtree(f"{NAME}_{VERSION}")
                else:
                    print('Aborting distribution...')
                    return
            # creating version folder is doesnt already exist
            os.makedirs(f"{NAME}_{VERSION}", exist_ok=True)
            # shutil.rmtree(f"{VERSION}{delim}{folder}")
            # os.makedirs(VERSION, exist_ok=True)

            shutil.rmtree(f"{NAME}_{VERSION}")
            os.makedirs(f"{NAME}_{VERSION}", exist_ok=True)
            os.chdir('../')

            # Get the directory path to the current gupy.py file without the filename
            gupy_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # get python location and executable
            if system == 'linux' or system == 'Linux':
                python_loc = gupy_file_path + '/python'
                python_folder = 'linux/bin'
                python_executable = 'python3.12'
            elif system == 'darwin':
                python_loc = gupy_file_path + '/python'
                python_folder = 'macos'
                python_executable = 'python3.12'
            else:
                python_loc = gupy_file_path + '\\python'
                python_folder = 'windows'
                python_executable =  'python.exe'

            # python_version = "".join(sys.version.split(' ')[0].split('.')[0:2]) 
            # print(os.getcwd())
            # moves files and folders - only checks the cythonized files in root directory.
            files = os.listdir(os.getcwd())
            for file_name in files:
                full_file_name = os.path.join(os.getcwd(), file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, f"dist/{NAME}_{VERSION}")
                elif os.path.isdir(full_file_name) and file_name != 'dist' and file_name != 'venv' and file_name != 'virtualenv' and file_name != 'node_modules':
                    shutil.copytree(full_file_name, f"dist/{NAME}_{VERSION}/{file_name}", dirs_exist_ok=True)
                print('Copied '+file_name+' to '+f"dist/{NAME}_{VERSION}/{file_name}"+'...')
            if not os.path.exists(f'dist/{NAME}_{VERSION}/{NAME}_app/static/logo'):
                print('Creating logo directory...')
                logo_directory = os.path.join(gupy_file_path, 'gupy_logo.png')       
                os.makedirs(f'dist/{NAME}_{VERSION}/{NAME}_app/static', exist_ok=True)
                os.makedirs(f'dist/{NAME}_{VERSION}/{NAME}_app/static/logo', exist_ok=True)
                shutil.copy(logo_directory, f'dist/{NAME}_{VERSION}/{NAME}_app/static/logo/gupy_logo.png')
            if not os.path.exists(f'dist/{NAME}_{VERSION}/{NAME}_app/static/splashscreen'):
                print('Creating splashscreen directory...')
                splashscreen_directory = os.path.join(gupy_file_path, 'gupy_splashscreen.png')       
                os.makedirs(f'dist/{NAME}_{VERSION}/{NAME}_app/static', exist_ok=True)
                os.makedirs(f'dist/{NAME}_{VERSION}/{NAME}_app/static/splashscreen', exist_ok=True)
                shutil.copy(splashscreen_directory, f'dist/{NAME}_{VERSION}/{NAME}_app/static/splashscreen/gupy_splashscreen.png')
            if not os.path.exists(f'dist/{NAME}_{VERSION}/{NAME}_app/static/icon'):
                print('Creating icon directory...')
                ico_directory = os.path.join(gupy_file_path, 'gupy.ico')       
                os.makedirs(f'dist/{NAME}_{VERSION}/{NAME}_app/static', exist_ok=True)
                os.makedirs(f'dist/{NAME}_{VERSION}/{NAME}_app/static/icon', exist_ok=True)
                shutil.copy(ico_directory, f'dist/{NAME}_{VERSION}/{NAME}_app/static/icon/gupy.ico')
            # package latest python if not selected - make python folder with windows/mac/linux
            os.makedirs(f"dist/{NAME}_{VERSION}/python", exist_ok=True)
            print('Copying python folder...')

            # import gupy_framework_windows_deps 
            # import gupy_framework_linux_deps
            # import gupy_framework_macos_deps
            # gupy_framework_windows_deps.add_deps(f"dist/{NAME}_{VERSION}/python")
            # gupy_framework_linux_deps.add_deps(f"dist/{NAME}_{VERSION}/python")
            # gupy_framework_macos_deps.add_deps(f"dist/{NAME}_{VERSION}/python/macos")
            # mac_pkg_file = gupy_framework_macos_deps.get_deps()[0]
            import py7zr
            archive_path = gupy_file_path + delim + 'python.7z'
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                archive.extractall(path=f"dist/{NAME}_{VERSION}")
            # shutil.copytree(python_loc, f"dist/{NAME}_{VERSION}/python", dirs_exist_ok=True)
            
            print('Copied python folder...')
            os.chdir(f'dist/{NAME}_{VERSION}')


            # command = f".{delim}python{delim}{python_folder}{delim}{python_executable} python{delim}{python_folder}{delim}get-pip.py"
            # # Run the command
            # result = subprocess.run(command, shell=True, check=True)

            # command = f".{delim}python{delim}{python_folder}{delim}{python_executable} -m pip install --upgrade pip"
            # # Run the command
            # result = subprocess.run(command, shell=True, check=True)

            # # install requirements with new python location if it exists
            # if os.path.exists('requirements.txt'):
            #         # Read as binary to detect encoding
            #     with open('requirements.txt', 'rb') as f:
            #         raw_data = f.read(10000)  # Read first 10KB
            #     detected = chardet.detect(raw_data)
            #     encoding = detected.get('encoding', 'utf-8')

            #     with open('requirements.txt', 'r', encoding=encoding) as f:
            #         if len(f.readlines()) > 0:
            #             command = f".{delim}python{delim}{python_folder}{delim}{python_executable} -m pip install -r requirements.txt"

            #             # Run the command
            #             result = subprocess.run(command, shell=True, check=True)
            #             # Check if the command was successful
            #             if result.returncode == 0:
            #                 print("Requirements installed successfully.")
            #             else:
            #                 print("Failed to install requirements.txt - ensure it exists.")

            # subprocess.run(f'.\\go\\bin\\go.exe mod tidy', shell=True, check=True)
            # Use glob to find all .ico files in the folder
            ico_files = glob.glob(os.path.join(f'{NAME}_app/static/icon', '*.ico'))
            ico = ico_files[0].replace('\\','/') 

            png_files = glob.glob(os.path.join(f'{NAME}_app/static/logo', '*.png'))
            png = png_files[0].replace('\\','/') # changing to forward slashes for mac/linux compatibility

            git_selection = input(f'Do you intend to upload this release to Github for automatic updates? (y/n): ')
            if git_selection.lower() == 'y':
                print("Please enter Github information for the app where your release package will be uploaded...")
                REPO_OWNER = input(f'Enter the Github repository owner: ')
                REPO_NAME = input("Enter the Github repository name: ")

            # create install.bat/sh for compiling run.go
            run_py_content = r'''
import sys
import os
import platform
import subprocess
import requests

import glob

import tkinter as tk
from PIL import Image, ImageTk  # pip install pillow

def show_splash(image_path, max_width=600, duration=3000):
    root = tk.Tk()
    root.overrideredirect(True)  # no window frame

    # Load image and compute target size
    img = Image.open(image_path)
    ow, oh = img.size
    # Cap width to max_width (dont upscale if smaller)
    tw = min(ow, max_width)
    th = int(round(oh * (tw / ow)))  # preserve aspect ratio

    # (Optional) ensure it fits vertically on very small screens
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    if th > int(sh * 0.9):           # too tall? scale down to 90% of screen height
        scale = (sh * 0.9) / th
        tw = int(round(tw * scale))
        th = int(round(th * scale))

    # Resize image to target size and create PhotoImage
    img = img.resize((tw, th), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    # Center the window
    x = (sw // 2) - (tw // 2)
    y = (sh // 2) - (th // 2)
    root.geometry(f"{tw}x{th}+{x}+{y}")

    # Fill the splash with the image
    label = tk.Label(root, image=photo, borderwidth=0, highlightthickness=0)
    label.image = photo  # keep a reference
    label.pack(fill="both", expand=True)

    root.after(duration, root.destroy)
    root.mainloop()

def get_screen_size():
    try:
        m = screeninfo.get_monitors()[0]
        return m.width, m.height
    except Exception:
        return 1920, 1080



def run_with_switches(system: str, url: str):
    import shutil
    sw, sh = get_screen_size()
    ww, wh = 1024, 768
    x = (sw - ww) // 2
    y = (sh - wh) // 2
    args = [
        f"--app={url}",
        "--disable-pinch",
        "--disable-extensions",
        "--guest",
        "--incognito",
        f"--window-size={ww},{wh}",
        f"--window-position={x},{y}",
    ]

    if system == "Windows":
        candidates = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                subprocess.Popen([c] + args)
                return
        print("Chromium-based browser not found.")
        return

    # macOS/Linux
    binaries = ["google-chrome", "chromium", "chromium-browser", "brave-browser", "microsoft-edge"]
    for b in binaries:
        p = shutil.which(b)
        if p:
            subprocess.Popen([p] + args)
            return
    import webbrowser
    webbrowser.open(url)

def get_platform_type():
    return platform.system()


def stop_previous_server():
    try:
        pid_path = os.path.join(os.path.expanduser("~"), "app_server.pid")
        if not os.path.exists(pid_path):
            return
        with open(pid_path, "r") as f:
            pid = int(f.read().strip())
        system = platform.system()
        if system == "Windows":
            cmd = f'taskkill /F /PID {pid}'
        else:
            cmd = f'kill -9 {pid}'
        subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        print(f"Error stopping previous server: {e}")


def get_latest_release(repo_owner, repo_name):
    """Fetch the latest release information from GitHub."""
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json().get("name") + ".zip"  # Get the release name
    except Exception as e:
        print(f"Error fetching latest release: {e}")
        return None

def main():
    # Add the current directory to sys.path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
'''
            if git_selection.lower() == 'y':
                run_py_content += r'''
    # Define the repository owner and name
    REPO_OWNER = "'''+REPO_OWNER+r'''"  # Replace with your GitHub repo owner
    REPO_NAME = "'''+REPO_NAME+r'''"    # Replace with your GitHub repo name

    # Check the current release version
    release_file = os.path.join(os.path.dirname(__file__), "release")
    current_release = None
    if os.path.exists(release_file):
        with open(release_file, "r") as f:
            current_release = f.read().strip()

    # Fetch the latest release version from GitHub
    latest_release = get_latest_release(REPO_OWNER, REPO_NAME)

    # Compare the current release with the latest release
    if latest_release and current_release != latest_release:
        print(f"New release available: {latest_release}. Updating...")

        # Determine the platform and run the appropriate install script
        system = platform.system()
        if system == "Windows":
            install_script = os.path.join(os.path.dirname(__file__), "install.bat")
            subprocess.run([install_script], shell=True)
        elif system in ["Linux", "Darwin"]:  # Darwin is macOS
            install_script = os.path.join(os.path.dirname(__file__), "install.sh")
            subprocess.run(["bash", install_script])
        else:
            print(f"Unsupported platform: {system}")
            sys.exit(1)

        # Exit the script after running the installer
        sys.exit(0)
'''
            run_py_content += r'''
    # Show the splash screen with the app logo
    # Define the path to the splashscreen folder
    splashscreen_folder = os.path.join(os.path.dirname(__file__), "static/splashscreen")

    # Find all .png files in the folder
    png_files = glob.glob(os.path.join(splashscreen_folder, "*.png"))

    # Check if any .png files exist
    if png_files:
        # Assign the first .png file to a variable
        file_to_use = png_files[0]
        show_splash(file_to_use, max_width=600, duration=3000)

    stop_previous_server()
    with open(os.path.join(os.path.expanduser("~"), "app_server.pid"), "w") as f:
        f.write(str(os.getpid()))

    system = get_platform_type()
    run_with_switches(system, "http://127.0.0.1:8000")

    if system == 'Darwin':
        system = 'mac'
    elif system == 'Linux':
        system = 'linux'
    else:
        system = 'windows'

    # Use the bundled Python
    exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python", system, "python.exe")
    if not os.path.exists(exe):
        exe = sys.executable  # fallback

    base = os.path.dirname(os.path.abspath(__file__))

    # Find manage.py and run from its directory
    candidates = [os.path.join(base, "manage.py")] + glob.glob(os.path.join(base, "**", "manage.py"), recursive=True)
    manage_py = next((p for p in candidates if os.path.exists(p)), None)
    if not manage_py:
        print("manage.py not found"); sys.exit(1)

    project_dir = os.path.dirname(manage_py)
    cmd = [exe, "manage.py", "runserver", "127.0.0.1:8000"]
    subprocess.check_call(cmd, cwd=project_dir)


if __name__ == "__main__":
    main()
                        '''
            bash_install_script_content = r'''
#!/bin/bash
'''
            if git_selection.lower() == 'y':
                bash_install_script_content += r'''
# Set repository owner and name
REPO_OWNER="'''+REPO_OWNER+r'''"
REPO_NAME="'''+REPO_NAME+r'''"

# GitHub API URL to fetch the latest release
API_URL="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"

# Fetch the JSON from the API
JSON=$(curl -s "$API_URL")

# Extract the browser_download_url from the first asset
DOWNLOAD_URL=$(echo "$JSON" | grep -o '"browser_download_url": *"[^"]*"' | head -n 1 | sed 's/"browser_download_url": *"//;s/"//')

# Extract the name from the asset - assuming the second occurrence of "name" is for the asset
LATEST_RELEASE=$(echo "$JSON" | grep -o '"name": *"[^"]*"' | head -n 2 | tail -n 1 | sed 's/"name": *"//;s/"//')


# Check if download URL is found
if [ -z "$DOWNLOAD_URL" ]; then
    echo "No download URL found. Exiting."
    exit 1
fi

# Read the current release file name from the 'release' file
if [ -f release ]; then
    CURRENT_RELEASE=$(cat release)
else
    CURRENT_RELEASE="NONE"
fi

# Print the current and latest release names
echo "CURRENT_RELEASE: $CURRENT_RELEASE"
echo "LATEST_RELEASE: $LATEST_RELEASE"

# Compare the current release with the latest release
if [ "$CURRENT_RELEASE" == "$LATEST_RELEASE" ]; then
    echo "Current release is up to date."
else


    # Echo the download URL (for verification)
    echo "Download URL: $DOWNLOAD_URL"

    # Download the zip file using curl
    echo "Downloading latest release..."
    curl -L "$DOWNLOAD_URL" -o "$LATEST_RELEASE"

    # Unzip the file into the current directory
    echo "Extracting the archive..."
    unzip -o "$LATEST_RELEASE" -d ./

    # Detect if the unzip created a new folder (dynamically)
    EXTRACTED_FOLDER=$(find . -maxdepth 1 -type d ! -name "." ! -name ".*" | head -n 1)
    if [ -n "$EXTRACTED_FOLDER" ] && [ "$EXTRACTED_FOLDER" != "." ]; then
        echo "Detected folder: $EXTRACTED_FOLDER"
        echo "Moving contents of $EXTRACTED_FOLDER to current directory..."
        mv "$EXTRACTED_FOLDER"/* ./
        rm -rf "$EXTRACTED_FOLDER"
    else
        echo "No separate directory detected; extraction complete."
    fi

    # Cleanup - remove downloaded zip file
    echo "Cleanup done. Removing downloaded zip file..."
    rm "$LATEST_RELEASE"

    # Update the 'release' file with the new release name
    echo "$LATEST_RELEASE" > release

    echo "Your folder has been updated."
    sleep 3
fi
'''
            bash_install_script_content += r'''
# Set the working directory to the script's directory
cd "$(dirname "$0")"
echo "Current directory is: $(pwd)"

# Determine the OS and current directory
OS=$(uname)
CURRENT_DIR=$(pwd)

if [ "$OS" = "Darwin" ]; then
    # Set desired Python version and installer file path
    PYTHON_VERSION="3.12.10"
    PKG_DIR="python/macos"
    PKG_FILE="python-${PYTHON_VERSION}-macos11.pkg"
    PKG_PATH="$PKG_DIR/$PKG_FILE"
    PKG_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/$PKG_FILE"
    
    # Ensure the pkg directory exists
    mkdir -p "$PKG_DIR"
    
    # On macOS: Install Python3.12 if not found using the pkg installer from the Python download site
    if ! command -v python3.12 &> /dev/null; then
        # Download the installer if it doesn't exist locally
        if [ ! -f "$PKG_PATH" ]; then
            echo "Python3.12 not found. Downloading installer from $PKG_URL..."
            curl -L "$PKG_URL" -o "$PKG_PATH"
            if [ $? -ne 0 ]; then
                echo "Failed to download Python3.12 installer."
                exit 1
            fi
        fi
        
        # Run the installer
        echo "Installing Python3.12 from $PKG_PATH..."
        sudo installer -pkg "$PKG_PATH" -target /
        if [ $? -ne 0 ]; then
            echo "Python3.12 installation from pkg failed."
            exit 1
        fi
        echo "Python3.12 successfully installed."
    fi
    # -- Install requirements.txt using Python --
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements from requirements.txt..."
        python3.12 -m pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "Failed to install requirements. Aborting."
            exit 1
        else
            echo "Requirements installed successfully."
        fi
    else
        echo "requirements.txt not found."
    fi
    # macOS: create a minimal AppleScript-based app that launches run.py
    APP_PATH="$HOME/Desktop/'''+NAME+r'''.app"
    echo "Creating macOS desktop shortcut at $APP_PATH"

    mkdir -p "$APP_PATH/Contents/MacOS"
    cat <<EOF > "$APP_PATH/Contents/MacOS/'''+NAME+r'''"
#!/bin/bash
# Change directory to the folder containing run.py
cd "$CURRENT_DIR"
# Run the Python script using the Python 3.12 interpreter
python3.12 "$CURRENT_DIR/run.py"

EOF
    chmod +x "$APP_PATH/Contents/MacOS/'''+NAME+r'''"
    # Create a minimal Info.plist file
    mkdir -p "$APP_PATH/Contents"
    cat <<EOF > "$APP_PATH/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>'''+NAME+r'''</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.'''+NAME+r'''</string>
    <key>CFBundleName</key>
    <string>'''+NAME+r'''</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>app_icon.icns</string>
</dict>
</plist>
EOF
    echo "Application updated. Now launch the app from the desktop shortcut!"
elif [ "$OS" = "Linux" ]; then
    # On Linux: ensure python3.12 is available
    sudo chmod +x python/linux/bin/python3.12
    python/linux/bin/python3.12 python/linux/bin/get-pip.py
    python/linux/python3.12 -m pip install --upgrade pip
    # -- Install requirements.txt using Python --
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements from requirements.txt..."
        python/linux/bin/python3.12 -m pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "Failed to install requirements. Aborting."
            exit 1
        else
            echo "Requirements installed successfully."
        fi
    else
        echo "requirements.txt not found."
    fi
    PYTHON_CMD="$CURRENT_DIR/python/linux/bin/python3.12"
    DESKTOP_FILE="$HOME/Desktop/'''+NAME+r'''.desktop"
    echo "Creating Linux desktop shortcut at $DESKTOP_FILE"
    cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name='''+NAME+r'''
Comment=Run '''+NAME+r'''
Exec=$PYTHON_CMD $CURRENT_DIR/run.py
Icon=$CURRENT_DIR/'''+png+r'''
Terminal=true
Type=Application
Categories=Utility;
EOF
    chmod +x "$DESKTOP_FILE"
    echo "Application updated. Now launch the app from the desktop shortcut!" &
else
    echo "Unsupported OS: $OS"
    exit 1
fi
        '''





            bat_install_script_content = r'''
@echo off
setlocal enabledelayedexpansion
'''
            if git_selection.lower() == 'y':
                bat_install_script_content += r'''
:: Set repository owner and name
set REPO_OWNER="'''+REPO_OWNER+r'''"
set REPO_NAME="'''+REPO_NAME+r'''"

:: GitHub API URL to fetch the latest release
set API_URL=https://api.github.com/repos/%REPO_OWNER%/%REPO_NAME%/releases/latest

:: Use PowerShell to fetch the latest release data and parse JSON to get the download URL and file name
for /f "delims=" %%i in ('powershell -Command "try { (Invoke-RestMethod -Uri '%API_URL%' -ErrorAction Stop).assets[0].browser_download_url } catch { Write-Output $_.Exception.Message; exit }"') do set DOWNLOAD_URL=%%i
for /f "delims=" %%j in ('powershell -Command "try { (Invoke-RestMethod -Uri '%API_URL%' -ErrorAction Stop).assets[0].name } catch { Write-Output $_.Exception.Message; exit }"') do set LATEST_RELEASE=%%j

:: Check if download URL is found
if not defined DOWNLOAD_URL (
    echo No download URL found. Exiting.
    exit /b 1
)

:: Read the current release file name from the 'release' file
if exist release (
    set /p CURRENT_RELEASE=<release
) else (
    set CURRENT_RELEASE=NONE
)

:: Print the current and latest release names
echo CURRENT_RELEASE: "%CURRENT_RELEASE%"
echo LATEST_RELEASE: "%LATEST_RELEASE%"

:: Compare the current release with the latest release
if "!CURRENT_RELEASE!" == "!LATEST_RELEASE!" (
    echo Current release is up to date.
) else (

    
    :: Echo the download URL (for verification)
    echo Download URL: !DOWNLOAD_URL!

    :: Download the zip file using PowerShell
    echo Downloading latest release...
    powershell -Command "Invoke-WebRequest -Uri '!DOWNLOAD_URL!' -OutFile '!LATEST_RELEASE!'"
    
    :: Unzip the file into the current directory
    echo Extracting the archive...
    powershell -Command "Expand-Archive -Path '!LATEST_RELEASE!' -DestinationPath '.' -Force"
    
    :: (Optional) If the archive extracts into a folder, move its contents to the current directory.
    :: You can add folder detection code here if desired.
    
    :: Cleanup - remove downloaded zip file
    echo Cleanup done. Removing downloaded zip file...
    del !LATEST_RELEASE!
    
    :: Update the 'release' file with the new release name
    echo !LATEST_RELEASE!>release
    
    echo Your folder has been updated.
    timeout /t 3 /nobreak >nul
)
'''
            bat_install_script_content += r'''

:: Install requirements if available
if exist requirements.txt (
    echo Installing requirements from requirements.txt...
    %~dp0python/windows/python.exe -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install requirements. Aborting.
        pause
        exit /b 1
    )
    echo Requirements installed successfully.
) else (
    echo requirements.txt not found.
)

:: Create VBScript to make a desktop shortcut to run "python run.py"
echo Creating desktop shortcut...
echo Set objShell = CreateObject("WScript.Shell") > CreateShortcut.vbs
echo Set desktopShortcut = objShell.CreateShortcut(objShell.SpecialFolders("Desktop") ^& "\\'''+ NAME +r'''.lnk") >> CreateShortcut.vbs
echo desktopShortcut.TargetPath = "%~dp0python/windows/python.exe" >> CreateShortcut.vbs
echo desktopShortcut.Arguments = "run.py" >> CreateShortcut.vbs
echo desktopShortcut.WorkingDirectory = "%cd%" >> CreateShortcut.vbs
echo desktopShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo desktopShortcut.Save >> CreateShortcut.vbs
echo Set dirShortcut = objShell.CreateShortcut("%cd%\\'''+ NAME +r'''.lnk") >> CreateShortcut.vbs
echo dirShortcut.TargetPath = "%~dp0python/windows/python.exe" >> CreateShortcut.vbs
echo dirShortcut.Arguments = "run.py" >> CreateShortcut.vbs
echo dirShortcut.WorkingDirectory = "%cd%" >> CreateShortcut.vbs
echo dirShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo dirShortcut.Save >> CreateShortcut.vbs

:: Run the VBScript to create the shortcuts, then clean up
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo Application updated. Now launch the app from the desktop shortcut!
pause
'''

            iss_contents = r'''
#define AppName "'''+NAME+r'''"
#define Version "'''+VERSION+r'''"
#define Icon "'''+ico+r'''"
#define Source "'''+os.getcwd()+r'''"

[Setup]
; Basic installer settings
AppName={#AppName}
AppVersion={#Version}
; Install under %USERPROFILE%\Downloads\AppFolderName
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
OutputBaseFilename={#AppName}_Setup
; Use a custom icon for the setup EXE
SetupIconFile={#Source}\{#Icon}
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x86 x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

[Files]
; Copy all files from your unpacked release folder
Source: "{#Source}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

; [Icons]
; Desktop shortcut
; Name: "{userdesktop}\{#AppName}.lnk"; \
    ; Filename: "{app}\python\windows\pythonw.exe"; \
    ; Parameters: """{app}\run.py"""; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\{#Icon}"; IconIndex: 0

; Shortcut in the application folder
; Name: "{app}\{#AppName}.lnk"; \
    ; Filename: "{app}\python\windows\pythonw.exe"; \
    ; Parameters: """{app}\run.py"""; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\{#Icon}"; IconIndex: 0

;[Run]
; Optionally launch the app after install
;Filename: "{app}\python\windows\pythonw.exe"; \
;    Parameters: """{app}\run.py"""; \
;    WorkingDir: "{app}"; \
;    Flags: nowait postinstall skipifsilent
[Run]
; Run install.bat after copying files
Filename: "{app}\install.bat"; \
Description: "Finalize installation"; \
WorkingDir: "{app}"; \
Flags: shellexec postinstall waituntilterminated skipifsilent
                '''
            with open('run.py', 'w') as f:
                f.write(run_py_content)
            # Write install.sh with LF encoding for Unix-based systems
            with open('install.sh', 'w', newline='\n') as f:
                f.write(bash_install_script_content)

            # Write install.bat with CRLF encoding for Windows
            with open('install.bat', 'w', newline='\r\n') as f:
                f.write(bat_install_script_content)
            with open('release', 'w') as f:
                f.write(f'{NAME}_{VERSION}.zip')
            with open(NAME+'_'+VERSION+'_Setup.iss', 'w', newline='\n') as f:
                f.write(iss_contents)

            # if self.lang == 'go':
            #     # # cythonize server.py
            #     # print(f'Building server.py file...')
            #     # os.system(f'cythonize -i server.py')
            #     # gopherize server.go
            #     print(f'Building server.go file...')
            #     os.system(f'go build -o server-{platform.system().lower()}.so -buildmode=c-shared server.go ')



            print(f'Files created successfully... \nNow compress the folder into a zip file and upload it to github releases (matching the zip filename in the release file; {NAME}_{VERSION}.zip). \nOptionally, you may install Inno Setup to create an installer with the {NAME}_{VERSION}_Setup.iss file.')



        except Exception as e:
            print('Error: '+str(e))
            return
