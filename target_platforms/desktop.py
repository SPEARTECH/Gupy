from . import base
import os
import platform
import glob

class Desktop(base.Base):
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
  <link rel="icon" href="{{url_for('static', filename='gupy_logo.png')}}" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle h-96 hover:-translate-y-2 ease-in-out transition" src="{{url_for('static', filename='gupy_logo.png')}}" />
        <br>
        <button class="btn bg-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/50 text-base-100">[[ message ]] </button>
      </div>
    </center>
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

        },
        computed:{

        }

    }).mount('#app')
  </script>
</html>      
'''

    server_content = '''
# Documentation:
#   https://flask.palletsprojects.com/en/3.0.x/

import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
import random
from flask import Flask, render_template, render_template_string, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
# import numpy as np
import random
import json

# WORKSAFE=False
# try:
#     from gevent.pywsgi import WSGIServer
# except Exception as e:
#     print(e)
#     WORKSAFE=True
        
def run_with_switches():
    # Check the default browser
    if os.path.exists("C:/Program Files/Google/Chrome/Application/chrome.exe"):
        command = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe", 
            '--app=http://127.0.0.1:8000', 
            '--disable-pinch', 
            '--disable-extensions', 
            '--guest'
        ]
        print("Running command:", command)
        subprocess.Popen(command)
        return
    elif os.path.exists("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"):
        command = [
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", 
            '--app=http://127.0.0.1:8000', 
            '--disable-pinch', 
            '--disable-extensions', 
            '--guest'
        ]
        print("Running command:", command)
        subprocess.Popen(command)
        return

    print("Chromium-based browser not found or default browser not set.")

def stop_previous_flask_server():
    try:
        # Read the PID from the file
        with open(f'{os.path.expanduser("~")}/flask_server.pid', 'r') as f:
            pid = int(f.read().strip())
        
        # # Check if the Flask server process is still running
        # while True:
        #     if not os.path.exists(f'/proc/{pid}'):
        #         break  # Exit the loop if the process has exited
        #     time.sleep(1)  # Sleep for a short duration before checking again

        # Terminate the Flask server process
        command = f'taskkill /F /PID {pid}'
        subprocess.run(command, shell=True, check=True)
        print("Previous Flask server process terminated.")
    except Exception as e:
        print(f"Error stopping previous Flask server: {e}")

app = Flask(__name__)

# getting the name of the directory
# where the this file is present.
path = os.path.dirname(os.path.realpath(__file__))


# Routes
@app.route('/')
def index():
    html = """
   
    """

    file_path = f'{os.path.dirname(os.path.realpath(__file__))}/templates/index.html'

    with open(file_path, 'r') as file:
        html = ''
        for line in file:
            html += line
            
        return render_template_string(html)
        # return render('index.html')

@app.route('/api/example_api_endpoint', methods=['GET'])
def example_api_endpoint():
    # Get the data from the request
    # data = request.json.get('data') # for POST requests with data
    from python_modules import python_modules
    go_message = python_modules.main()

    data = {'Go Module Message':go_message}

    # Perform data processing

    # Return the modified data as JSON
    return jsonify({'result': data})

if __name__ == '__main__':
    stop_previous_flask_server()

    pid_file = f'{os.path.expanduser("~")}/flask_server.pid'
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))  # Write the PID to the file
    
    # ADD SPLASH SCREEN?

    # Run Apped Chrome Window
    run_with_switches()

    # if WORKSAFE == False:
    #     http_server = WSGIServer(("127.0.0.1", 8000), app)
    #     http_server.serve_forever()
    # else:
    app.run(debug=True, threaded=True, port=8000, use_reloader=False)  

    '''

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

    read_me = '''

    '''
    
    def __init__(self, name, lang=''):
        self.name = name
        self.lang = lang
        self.folders = [
          f'apps/{self.name}/desktop', 
          f'apps/{self.name}/desktop/dev', 
          f'apps/{self.name}/desktop/dev/templates',
          f'apps/{self.name}/desktop/dev/static',
        ]

        if self.lang == 'go':
            self.server_content = '''
package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
    "fmt"
    "io/ioutil"
    "os/exec"
)

func main() {
	r := gin.Default()

	// Routes
	r.GET("/", index)

	// Start the server
	go openChrome("http://127.0.0.1:8080") // Open Chrome with your server URL
	r.Run(":8080")
}

func index(c *gin.Context) {
	// Load the HTML template
	htmlPath := "./templates/index.html"
	htmlContent, err := ioutil.ReadFile(htmlPath)
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to load HTML template")
		return
	}

	// Render the HTML template
	c.Data(http.StatusOK, "text/html; charset=utf-8", htmlContent)
}

func openChrome(url string) {
	cmd := exec.Command("C:/Program Files/Google/Chrome/Application/chrome.exe", "--app=" + url, "--disable-pinch", "--disable-extensions", "--guest")
	err := cmd.Start()
	if err != nil {
		fmt.Println("Failed to open Chrome:", err)
	}
}


            '''

        self.files = {
            f'apps/{self.name}/desktop/dev/templates/index.html': self.index_content,
            }

        if self.lang == 'py':
            self.files[f'apps/{self.name}/desktop/dev/server.py'] = self.server_content
            self.folders.append(f'apps/{self.name}/desktop/dev/python_modules')
            self.files[f'apps/{self.name}/desktop/dev/python_modules/python_modules.py'] = self.python_modules_content
            self.folders.append(f'apps/{self.name}/desktop/dev/go_modules')
            self.files[f'apps/{self.name}/desktop/dev/go_modules/go_modules.go'] = self.go_modules_content
        else:
            self.files[f'apps/{self.name}/desktop/dev/server.go'] = self.server_content

    def create(self):
        for folder in self.folders:
            if not os.path.exists(folder):
                os.mkdir(folder)
                print(f'created "{folder}" folder.')
            else:
                print(f'"{folder}" already exists.\nAborting...')
                return
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()
        if self.lang == 'py':
            os.chdir(f'apps/{self.name}/desktop/dev/go_modules/')
            os.system(f'go mod init example/go_modules')
        else:
            os.chdir(f'apps/{self.name}/desktop/dev/')
            os.system(f'go mod init example/server')
            os.system(f'go mod tidy')
        # system = platform.system()

        # if system == 'Darwin':
        #     cmd = 'cp'
        # elif system == 'Linux':
        #     cmd = 'cp'
        # else:
        #     cmd = 'copy'
        import shutil
        os.chdir(f'cd ../../../../../../../')
        shutil.copy('gupy_logo.png', f'apps/{self.name}/desktop/dev/static/gupy_logo.png')

    def run(self,name):
        if os.path.exists(f'apps/{name}/desktop/dev/server.py'):
            # add check here for platform type and language 
            system = platform.system()

            if system == 'Darwin':
                cmd = 'python3'
            elif system == 'Linux':
                cmd = 'python'
            else:
                cmd = 'python'

            os.system(f'{cmd} apps/{name}/desktop/dev/server.py')
        else:
            os.chdir(f'apps/{name}/desktop/dev')
            os.system(f'go mod tidy')
            os.system(f'go run server.go')

    def compile(self,name):
        if os.path.exists(f'apps/{name}/desktop/dev/server.py'):
            if not os.path.exists(f'apps/{name}/desktop/dist'):
                os.mkdir(f'../dist')
            os.chdir(f'apps/{name}/desktop/dev/')
            os.system(f'nuitka --output-dir=../dist --disable-console')
        elif os.path.exists(f'apps/{name}/desktop/dev/server.go'):
            if not os.path.exists(f'apps/{name}/desktop/dist'):
                os.mkdir(f'apps/{name}/desktop/dist')
            os.chdir(f'apps/{name}/desktop/dev/')
            os.system(f'go mod tidy')
            # os.chdir(f'../dist')
            os.system(f'go build')

    def cythonize(self,name):
        if os.path.exists(f"apps/{name}/desktop/dev/python_modules") and os.path.exists(f"apps/{name}/desktop/dev/server.py"):
            os.chdir(f'apps/{name}/desktop/dev/python_modules')
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
        if os.path.exists(f"apps/{name}/desktop/dev/go_modules") and os.path.exists(f"apps/{name}/desktop/dev/server.py"):
            os.chdir(f'apps/{name}/desktop/dev/go_modules')
            os.system(f'go mod tidy')
            files = [f for f in glob.glob('*.go')]
            for file in files:
                print(f'Building {file} file...')
                os.system(f'go build -o {os.path.splitext(file)[0]}.so -buildmode=c-shared {file} ')

    # Add Assemble