from . import base
import os
import platform
import subprocess
import shutil
import glob

class Pwa(base.Base):
    index_content = '''

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
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js', { scope: '/' });
  }
</script>
<script src="go_modules/wasm_exec.js"></script>
  <script>
    const { createApp } = Vue
    
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
          const go = new Go();
          WebAssembly.instantiateStreaming(fetch("go_modules/go_module.wasm"), go.importObject).then((result) => {
            go.run(result.instance);
          });

          let worker = new Worker('worker.js');
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

    sw_content = '''
const CACHE_NAME = `app-v1`;

// Use the install event to pre-cache all initial resources.
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    cache.addAll([
      '/',
    ]);
  })());
});

self.addEventListener('fetch', event => {
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);

    // Get the resource from the cache.
    const cachedResponse = await cache.match(event.request);
    if (cachedResponse) {
      return cachedResponse;
    } else {
        try {
          // If the resource was not in the cache, try the network.
          const fetchResponse = await fetch(event.request);

          // Save the resource in the cache and return it.
          cache.put(event.request, fetchResponse.clone());
          return fetchResponse;
        } catch (e) {
          // The network failed.
        }
    }
  })());
});
'''
    
    worker_content = '''
onmessage = function(message){
    message.data['message'] = 'This is from the worker!'

    // console.log(message.data)

    postMessage(message.data)
}  

    '''

    go_module_content = '''
package main

import "fmt"

func main() {
	fmt.Println("Hello, from Go WebAssembly!")
}
    '''

    def __init__(self, name):
        self.name = name
        self.manifest_content = '''
{
    "lang": "en-us",
    "name": "'''+self.name+'''",
    "short_name": "'''+self.name+'''",
    "description": "",
    "start_url": "/",
    "background_color": "#2f3d58",
    "theme_color": "#2f3d58",
    "orientation": "any",
    "display": "standalone",
    "icons": [
        {
            "src": "",
            "type": "image/png",
            "sizes": "512x512"
        }
    ]
}
'''

        self.folders = [
            f'apps/{self.name}/pwa',
            f'apps/{self.name}/pwa/go_modules',
            # f'apps/{self.name}/pwa/python_modules',

            ]
        self.files = {
            f'apps/{self.name}/pwa/index.html': self.index_content,
            f'apps/{self.name}/pwa/manifest.js': self.manifest_content,
            f'apps/{self.name}/pwa/sw.js': self.sw_content,
            f'apps/{self.name}/pwa/worker.js': self.worker_content,
            f'apps/{self.name}/pwa/go_modules/go_module.go': self.go_module_content,
            }

    def create(self):
        for folder in self.folders:
            os.mkdir(folder)
            print(f'created "{folder}" folder.')
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()

        shutil.copy('gupy_logo.png', f'apps/{self.name}/pwa/gupy_logo.png')

        os.chdir(f'apps/{self.name}/pwa/go_modules')
        os.system(f'go mod init example/go_module')
        os.system(f'go mod tidy')
        def build_wasm():
          # Set the environment variables
          env = os.environ.copy()
          env['GOOS'] = 'js'
          env['GOARCH'] = 'wasm'
          
          # Command to execute
          command = 'go build -o go_module.wasm'
          
          # Execute the command
          result = subprocess.run(command, shell=True, env=env)
          
          # Check if the command was successful
          if result.returncode == 0:
              print("Build successful.")
          else:
              print("Build failed.")

        build_wasm()
        # os.system(f"$env:GOOS='js'; $env:GOARCH='wasm'; go build -o main.wasm")
        # Function to get the GOROOT environment variable using the 'go env' command
        def get_goroot():
            # Run 'go env GOROOT' command and capture the output
            result = subprocess.run(["go", "env", "GOROOT"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()  # Remove any surrounding whitespace/newlines
            else:
                raise Exception("Failed to get GOROOT: " + result.stderr)
        goroot = get_goroot()
        # Construct the path to wasm_exec.js
        wasm_exec_path = goroot + "/misc/wasm/wasm_exec.js"
        # Copy wasm_exec.js to the current directory
        shutil.copy(wasm_exec_path, '.')
        # shutil.copy("$(go env GOROOT)/misc/wasm/wasm_exec.js", '.')
        os.chdir(f'../')

    # launch index file in browser
    def run(self, name):
      os.chdir(f'apps/{name}/pwa')
      # add check here for platform type and language 
      system = platform.system()

      if system == 'Darwin':
          cmd = 'python3'
      elif system == 'Linux':
          cmd = 'python'
      else:
          cmd = 'python'

      os.system(f'{cmd} -m http.server')

    # def cythonize(self, name):
    #   pass

    def assemble(self, name):
        os.chdir(f'apps/{name}/pwa/go_modules')
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
              print("Build successful.")
          else:
              print("Build failed.")
        files = [f for f in glob.glob('*.go')]
        for filename in files:
          build_wasm(filename)

        # add assembly of cython modules

    
