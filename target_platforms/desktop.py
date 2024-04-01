from . import base
import os
import platform

class Desktop(base.Base):
    index_content = '''
<!DOCTYPE html>
<html>
<head>
  <title>Raptor App</title>
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
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='50' height='50' viewBox='0 0 400.000000 400.000000'%3E%3Cg transform='translate(0.000000,400.000000) scale(0.100000,-0.100000)' fill='%23000000' stroke='none'%3E%3Cpath d='M1835 3894 c-794 -81 -1441 -618 -1659 -1381 -64 -223 -86 -518 -57 -756 68 -549 381 -1047 856 -1360 155 -102 377 -199 562 -246 188 -48 479 -70 653 -51 589 64 1095 379 1422 886 47 72 145 276 178 369 180 511 133 1099 -127 1563 -94 167 -179 278 -323 422 -168 169 -303 267 -505 366 -277 135 -479 184 -775 189 -102 2 -203 1 -225 -1z m383 -284 c340 -41 662 -195 916 -440 248 -239 400 -515 469 -854 19 -95 22 -142 22 -321 -1 -179 -4 -225 -23 -313 -91 -416 -306 -754 -640 -1002 -210 -157 -439 -252 -722 -301 -117 -21 -414 -18 -535 5 -586 109 -1073 531 -1254 1086 -62 188 -75 274 -75 500 -1 226 15 340 76 524 29 89 127 297 154 327 8 8 14 18 14 22 0 11 87 130 124 171 20 21 36 40 36 43 0 9 114 122 135 133 13 7 22 17 19 22 -3 4 1 8 9 8 7 0 26 14 43 31 16 17 58 49 94 72 36 23 75 48 85 55 24 15 224 112 231 112 4 0 20 6 37 13 61 26 102 39 144 46 23 4 48 12 55 18 11 9 79 20 288 46 62 8 217 6 298 -3z'/%3E%3Cpath d='M950 2910 c0 -12 8 -21 23 -24 12 -3 34 -7 49 -10 15 -4 39 -17 54 -29 36 -31 40 -82 25 -314 -6 -98 -22 -362 -36 -588 -28 -465 -30 -484 -55 -542 -22 -50 -58 -71 -138 -81 -48 -6 -57 -10 -57 -27 0 -19 8 -20 273 -23 l272 -2 0 23 c0 21 -7 25 -61 35 -70 13 -120 46 -139 92 -14 33 -15 12 35 820 14 223 25 413 25 423 0 38 23 13 59 -65 21 -46 114 -240 206 -433 92 -192 184 -386 205 -430 139 -296 221 -456 236 -462 39 -15 13 -66 419 807 106 228 214 459 239 514 26 54 49 96 52 93 10 -10 87 -1203 80 -1242 -12 -64 -79 -109 -181 -121 -50 -6 -56 -9 -53 -28 3 -21 5 -21 338 -21 333 0 335 0 338 21 3 20 -3 22 -68 26 -126 9 -142 36 -160 266 -27 350 -80 1133 -80 1188 0 73 14 90 80 99 82 11 90 14 90 35 0 20 -6 20 -195 18 l-195 -3 -81 -170 c-44 -93 -99 -208 -121 -255 -22 -47 -100 -211 -173 -365 -73 -154 -160 -337 -193 -407 -34 -71 -65 -128 -70 -128 -5 0 -38 62 -75 138 -36 75 -96 200 -132 277 -37 77 -87 181 -110 230 -23 50 -61 128 -83 175 -22 47 -86 180 -140 295 l-100 210 -201 3 c-195 2 -201 2 -201 -18z'/%3E%3C/g%3E%3C/svg%3E" type="image/svg+xml">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  </head>
<body>
  <div id="app" style="text-align: center;">
    <button class="btn btn-primary">[[ message ]] </button>
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
            message: 'Welcome to Raptor!',
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
            })
            .finally(function () {
                // always executed
            });
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

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from flask import Flask, render_template, render_template_string, request, jsonify

app = Flask(__name__)


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
            
        # return render('index.html')
        return render_template_string(html)

@app.route('/api/example_api_endpoint', methods=['GET'])
def example_api_endpoint():
    # Get the data from the request
    # data = request.json.get('data') # for POST requests with data
    data = {'welcome to':'Raptor!'}

    # Perform data processing


    # Return the modified data as JSON
    return jsonify({'result': data})


if __name__ == '__main__':   
    pid_file = f'{os.path.expanduser("~")}/flask_server.pid'
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))  # Write the PID to the file

    app.run(debug=True)    
    '''

    main_content = '''


import subprocess
import os
from flask import Flask
import time


def run_with_switches():
    # Check the default browser
    if os.path.exists("C:\Program Files\Google\Chrome\Application\chrome.exe"):
        command = [
            "C:\Program Files\Google\Chrome\Application\chrome.exe", 
            '--app=http://localhost:5000', 
            '--disable-pinch', 
            '--disable-extensions', 
            '--guest'
        ]
        print("Running command:", command)
        subprocess.Popen(command)
        return
    elif os.path.exists("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        command = [
            "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", 
            '--app=http://localhost:5000', 
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

if __name__ == '__main__':
    stop_previous_flask_server()
    
    subprocess.Popen(['python', f'{os.path.dirname(os.path.realpath(__file__))}/server/server.py'])
    # subprocess.Popen(['python', f'./server/server.py'])
    run_with_switches()



'''

    read_me = '''

    '''
    
    def __init__(self, name, lang):
        self.name = name
        self.lang = lang
        if self.lang == 'go':
          self.server_content = '''
          
          '''

        self.folders = [
          f'apps/{self.name}/desktop', 
          f'apps/{self.name}/desktop/dev', 
          f'apps/{self.name}/desktop/dev/server',
          f'apps/{self.name}/desktop/dev/server/templates',]

        self.files = {
            f'apps/{self.name}/desktop/dev/main.py': self.main_content,
            f'apps/{self.name}/desktop/dev/server/templates/index.html': self.index_content,
            f'apps/{self.name}/desktop/dev/server/server.py'\
               if self.lang == 'py' else \
            f'apps/{self.name}/desktop/dev/server/server.go': self.server_content\
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

    def run(self,name):
        # add check here for platform type and language 
        if self.lang == 'py':
          system = platform.system()

          if system == 'Darwin':
              cmd = 'python3'
          elif system == 'Linux':
              cmd = 'python'
          else:
              cmd = 'python'

        # os.system(f'{cmd} {name}/desktop/dev/server/server.py')
        os.system(f'{cmd} apps/{name}/desktop/dev/main.py')