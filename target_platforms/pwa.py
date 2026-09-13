from . import base
import os
import platform
import subprocess
import shutil
import glob
import sys
import click
from colorama import Fore, Style
import webbrowser

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
            print(f"Copied wasm_exec.js from: {src} to: {dest}")
            return True

    print("wasm_exec.js not found under your GOROOT.")
    print(f"Tried: {candidates}")
    print("Please install/reinstall the latest Go from https://go.dev/dl, then re-run.")
    return False


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
  <link rel="icon" href="/static/logo/gupy_logo.png" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  <script src="/static/go_wasm/wasm_exec.js")"></script>
  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle  h-96 w-96 max-h-full max-w-full object-contain  hover:-translate-y-2 ease-in-out transition" src="./static/logo/gupy_logo.png" />
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
                class=" btn btn-sm bg-blue-500  text-white  shadow-lg  hover:bg-blue-500/50 shadow-blue-500/50 hover:shadow-xl hover:shadow-blue-500/50 hover:-translate-y-0.5 no-animation"
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
     import { loadGoWasm } from './go_wasm.js';
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
            axios.get('/api/example_api_endpoint')
            .then((response) => {
                // handle success
                console.log(response);
                this.data = JSON.parse(JSON.stringify(response['data']))
                console.log(this.data)
            })
            .catch((error) => {
          console.log("decode:", error.message, error);
          const msg = this.pyodide_msg; // capture before async
            // use pyodide instead of api example
          (async () => {
              const pyodide = await loadPyodide();
            pyodide.registerJsModule("mymodule", { pyodide_msg: msg });
            await pyodide.loadPackage("numpy");
            const json = await pyodide.runPython(`
import json, mymodule
pyodide_msg = mymodule.pyodide_msg
pyodide_msg = 'This is the changed pyodide message!'
json.dumps({'new_msg': pyodide_msg})
`);
            const parsed = JSON.parse(json);
            console.log(parsed.new_msg);
          })().catch(e => console.log('An error occurred: ', e));
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

          let worker = new Worker('worker.js');
          worker.postMessage({ message: '' });
          worker.onmessage = (message) => {
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
        self.folders = [
            f'pwa',
            # f'gupy_apps/{self.name}/pwa/python_wasm',
            f'pwa/static',
            f'pwa/static/go_wasm',
            f'pwa/static/logo',
            f'pwa/static/splashscreen',
            f'pwa/static/icon',

            ]
        self.files = {
            f'pwa/index.html': self.index_content,
            f'pwa/manifest.js': self.manifest_content,
            f'pwa/sw.js': self.sw_content,
            f'pwa/worker.js': self.worker_content,
            f'pwa/go_wasm.js': self.go_wasm_js_content,
            f'pwa/static/go_wasm/go_wasm.go': self.go_wasm_content,
            }

    def create(self):
        import shutil
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

        for folder in self.folders:
            os.mkdir(folder)
            print(f'created "{folder}" folder.')
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()


        os.chdir(f'pwa/static/go_wasm')
        os.system(f'go mod init example/go_wasm')
        os.system(f'go mod tidy')
        # def build_wasm():
        #     # Set the environment variables
        #     env = os.environ.copy()
        #     env['GOOS'] = 'js'
        #     env['GOARCH'] = 'wasm'
            
        #     # Command to execute
        #     command = 'go build -o go_wasm.wasm'
            
        #     # Execute the command
        #     result = subprocess.run(command, shell=True, env=env)
            
        #     # Check if the command was successful
        #     if result.returncode == 0:
        #         print(f"{Fore.GREEN}Build successful.{Style.RESET_ALL}")
        #     else:
        #         print(f"{Fore.RED}Build failed.{Style.RESET_ALL}")

        # build_wasm()
        # os.system(f"$env:GOOS='js'; $env:GOARCH='wasm'; go build -o main.wasm")
        # Function to get the GOROOT environment variable using the 'go env' command
        # def get_goroot():
        #     # Run 'go env GOROOT' command and capture the output
        #     result = subprocess.run(["go", "env", "GOROOT"], capture_output=True, text=True)
        #     if result.returncode == 0:
        #         return result.stdout.strip()  # Remove any surrounding whitespace/newlines
        #     else:
        #         raise Exception("Failed to get GOROOT: " + result.stderr)
        # goroot = get_goroot()
        # # Construct the path to wasm_exec.js
        # wasm_exec_path = goroot + "/misc/wasm/wasm_exec.js"
        # # Copy wasm_exec.js to the current directory
        # shutil.copy(wasm_exec_path, '.')
        # shutil.copy("$(go env GOROOT)/misc/wasm/wasm_exec.js", '.')
        os.chdir(f'../../../')
        self.assemble()
        print(os.getcwd())
        # Get the directory of the current script
        current_directory = os.path.dirname(os.path.abspath(__file__))

        logo_directory = os.path.join(os.path.dirname(current_directory), 'gupy_logo.png')       
        
        shutil.copy(logo_directory, f'pwa/static/logo/gupy_logo.png')

        splashscreen_directory = os.path.join(os.path.dirname(current_directory), 'gupy_splashscreen.png')       
        
        shutil.copy(splashscreen_directory, f'pwa/static/splashscreen/gupy_splashscreen.png')

        ico_directory = os.path.join(os.path.dirname(current_directory), 'gupy.ico')       
        
        shutil.copy(ico_directory, f'pwa/static/icon/gupy.ico')

    # launch index file in browser
    def run(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'
        # assign current python executable to use
        cmd = sys.executable.split(delim)[-1]
        # Open the URL in the default web browser
        webbrowser.open("http://127.0.0.1:8000")
        os.system(f'{cmd} -m http.server -b 127.0.0.1 8000')

      # def cythonize(self, name):
      #   pass
 
    def assemble(self):
        ensure_wasm_exec(dest_dir=os.path.join("pwa", "static", "go_wasm"))    
        # detect if currently in go_wasm, otherwise, cd to go_wasm to run cmds
        os.chdir(f'pwa/static/go_wasm')
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
        os.chdir(f'../../../')
        # add assembly of cython modules

    def distribute(self, NAME, VERSION):
        try:

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

            # # Get the directory path to the current gupy.py file without the filename
            # gupy_file_path = os.path.dirname(os.path.abspath(__file__))

            # python_version = "".join(sys.version.split(' ')[0].split('.')[0:2]) 
            # print(os.getcwd())
            # moves files and folders - only checks the cythonized files in root directory.
            files = os.listdir(os.getcwd())
            for file_name in files:
                full_file_name = os.path.join(os.getcwd(), file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, f"dist/{NAME}_{VERSION}")
                elif os.path.isdir(full_file_name) and file_name != NAME and file_name != 'dist' and file_name != 'venv' and file_name != 'virtualenv':
                    shutil.copytree(full_file_name, f"dist/{NAME}_{VERSION}/{file_name}", dirs_exist_ok=True)
                print('Copied '+file_name+' to '+f"dist/{NAME}_{VERSION}/{file_name}"+'...')

            os.chdir(f'dist/{NAME}_{VERSION}')

            bash_install_script_content = r'''#!/bin/bash

# change to script’s directory
cd "$(dirname "$0")"

# open default browser
case "$(uname)" in
  Darwin*)
    open "http://localhost:${1:-8080}"
    ;;
  *)
    xdg-open "http://localhost:${1:-8080}" >/dev/null 2>&1
    ;;
esac

# serve files
PORT=${1:-8080}
DOCROOT=${2:-.}
echo "Serving $DOCROOT on http://localhost:$PORT/"

while true; do
  # read one HTTP request
  request=$(nc -l -p "$PORT" -q 1)
  path=$(printf '%s\n' "$request" | head -n1 | cut -d' ' -f2)
  [[ "$path" == "/" ]] && path="index.html"

  file="$DOCROOT/$path"
  if [[ -f "$file" ]]; then
    mime=$(file --brief --mime-type "$file")
    {
      printf 'HTTP/1.1 200 OK\r\n'
      printf 'Content-Type: %s\r\n' "$mime"
      printf 'Service-Worker-Allowed: /\r\n'
      printf '\r\n'
      cat "$file"
    } | nc -l -p "$PORT" -q 1
  else
    printf 'HTTP/1.1 404 Not Found\r\n\r\n'
  fi | nc -l -p "$PORT" -q 1
done
'''


            import base64

            # … inside Pwa.distribute() just before writing run.bat …

            # 1) your raw PowerShell listener script
            ps = r"""param(
  [int]$Port = 8080,
  [string]$Root = (Get-Location)
)

# minimal MIME map, now including wasm
$mimes = @{
  '.html' = 'text/html'
  '.htm'  = 'text/html'
  '.js'   = 'text/javascript'
  '.css'  = 'text/css'
  '.json' = 'application/json'
  '.png'  = 'image/png'
  '.jpg'  = 'image/jpeg'
  '.jpeg' = 'image/jpeg'
  '.gif'  = 'image/gif'
  '.svg'  = 'image/svg+xml'
  '.wasm' = 'application/wasm'
}

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()
Write-Host "Serving $Root on http://localhost:$Port/ (Ctrl+C to stop)"

while ($listener.IsListening) {
  $ctx   = $listener.GetContext()
  $rel   = $ctx.Request.Url.AbsolutePath.TrimStart('/')
  if ($rel -eq '') { $rel = 'index.html' }
  $file  = Join-Path $Root $rel

  if (Test-Path $file) {
    $bytes = [IO.File]::ReadAllBytes($file)
    $ext   = [IO.Path]::GetExtension($file).ToLower()
    $type  = $mimes[$ext]
    if (-not $type) { $type = 'application/octet-stream' }

    $ctx.Response.ContentType = $type
    # allow ServiceWorker scope
    $ctx.Response.AddHeader("Service-Worker-Allowed","/")
    $ctx.Response.StatusCode  = 200
    $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  } else {
    $ctx.Response.StatusCode = 404
  }
  $ctx.Response.Close()
}

pause
"""

            # 2) Base64-encode it as UTF-16LE (what PowerShell expects)
            b64 = base64.b64encode(ps.encode('utf-16le')).decode('ascii')


            bat_install_script_content = f'''
@echo off
rem — open default browser at localhost:8080 —
start "" "http://localhost:8080"

rem — one‐line launch of your listener —
powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {b64}

'''

            # Write run.sh with LF encoding for Unix-based systems
            with open('run.sh', 'w', encoding='utf-8', newline='\n') as f:
                f.write(bash_install_script_content)

            # Write run.bat with CRLF encoding for Windows
            with open('run.bat', 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(bat_install_script_content)
            with open('release', 'w') as f:
                f.write(f'{NAME}_{VERSION}.zip')

            print(f'Files created successfully... \nNow compress the folder into a zip file and upload it to github releases (matching the zip filename in the release file; {NAME}_{VERSION}.zip). \nOptionally, you may install Inno Setup to create an installer with the {NAME}_{VERSION}_Setup.iss file.')


        except Exception as e:
            print('Error: '+str(e))
            return
