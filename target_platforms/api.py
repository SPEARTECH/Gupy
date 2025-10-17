from . import base
import os
FAST_API_content = '''


    '''

FIBER_content = '''

'''

from . import base
import os
import platform
import glob
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

class Api(base.Base):
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
  <link rel="icon" href="{{url_for('static', path='logo/gupy_logo.png')}}" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  <script src="{{ url_for('static', path='go_wasm/wasm_exec.js') }}"></script>

  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle  h-96 w-96 max-h-full max-w-full object-contain  hover:-translate-y-2 ease-in-out transition" src="{{url_for('static', path='logo/gupy_logo.png')}}" />
        <br>
        <br>
        <button class="btn bg-blue-500 border-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-md hover:shadow-blue-500/50 text-base-100 shadow-none transition-shadow ">[[ message ]] </button>
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
<!-- <script>
  const ws = new WebSocket('ws://' + location.hostname + ':8765');
  // (Optional) log
  ws.onopen = () => console.log('WS open');
  ws.onclose = () => console.log('WS closed (server will exit)');
  // Ensure a clean close when tab/window goes away
  window.addEventListener('beforeunload', () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
  });</script> -->
<!-- <script>
  // When the user is leaving, use sendBeacon to notify the server to shut down.
  window.addEventListener('beforeunload', () => {
    navigator.sendBeacon('/shutdown');
  });
</script> -->  
<script type="module">
    const { createApp } = Vue
     import { loadGoWasm } from '{{url_for('static', path='go_wasm.js')}}';
    
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
            .then((response) => {
                // handle success
                console.log(response);
                this.data = response.data.result;
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

          let worker = new Worker("{{url_for('static', path='worker.js')}}");
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

    server_content = r'''
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import ctypes
from fastapi.responses import JSONResponse

app = FastAPI()

# paths
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Serve ./static at /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Point Jinja to ./templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# example API endpoint used by your HTML (axios.get('/api/example_api_endpoint'))
@app.get("/api/example_api_endpoint")
async def example_api_endpoint():
    try:
        # Python module
        from python_modules import python_modules
        py_message = python_modules.main()

        # Go c-shared lib
        path = BASE_DIR
        go_path = os.path.join(path, "go_modules", "go_modules.so")
        go_modules = ctypes.CDLL(go_path)
        go_modules.go_module.restype = ctypes.c_char_p
        go_message = go_modules.go_module().decode("utf-8")

        data = {"Python Module Message": py_message, "Go Module Message": go_message}
        return JSONResponse({"result": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ...existing code...
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
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


    read_me = ''' 

    '''
    
    init_content = '''
import sys
import os
# Add the parent directory of 'target_platforms' to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))'''

    def __init__(self, name, lang='go'):
        self.name = name
        self.lang = lang
        self.folders = [
          f'api', 
          f'api/static',
          f'api/static/go_wasm',
          # f'{self.name}/api/dev/templates/python_wasm',
          f'api/static/logo',
          f'api/static/splashscreen',
          f'api/static/icon',
          f'api/templates',
        ]
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
        self.go_server_content = r'''
'''

        self.worker_content = '''

onmessage = function(message){
    message.data['message'] = 'This is from the worker!'

    // console.log(message.data)

    postMessage(message.data)
}  
'''

        if self.lang == 'go':
            self.index_content = '''

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
  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle  h-96 w-96 max-h-full max-w-full object-contain  hover:-translate-y-2 ease-in-out transition" src="/static/logo/gupy_logo.png" />
        <br>
        <br>
        <button class="btn bg-blue-500 border-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-md hover:shadow-blue-500/50 text-base-100 shadow-none transition-shadow ">[[ message ]] </button>
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
(function(){
  const ws = new WebSocket('ws://' + location.hostname + ':8765');
  ws.onopen = () => console.log('WS open');
  ws.onclose = () => console.log('WS closed');
  window.addEventListener('beforeunload', () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
  });
})();
  </script>

  <script type="module">
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
          axios.get('/api/run_py?name=hello&arg=foo&arg=bar')
            .then(res => console.log('py result:', res.data))
            .catch(err => console.error(err));

      },
        async mounted() {

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

            self.go_server_content = r'''



// Build:
//   Linux:   go build -buildmode=c-shared -o mylib.so
//   macOS:   go build -buildmode=c-shared -o mylib.dylib
//   Windows: go build -buildmode=c-shared -o mylib.dll
package main

/*
#include <stdint.h>
*/
import "C"

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"time"
    "os/exec"
    "runtime"
)

var (
	srvMu sync.Mutex
	srv   *http.Server
)

// buildMux serves:
//   - "/" -> <staticDir>/index.html
//   - "/static/*" -> files from <staticDir>
//   - "/api/echo"
//   - "/healthz"
func buildMux(staticDir string) http.Handler {
	mux := http.NewServeMux()

	// Static directory server
	fs := http.FileServer(http.Dir(staticDir))
	mux.Handle("/static/", http.StripPrefix("/static/", fs))

	// Root -> index.html
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
        parent := filepath.Dir(filepath.Clean(staticDir))            // remove last folder
        idx := filepath.Join(parent, "templates", "index.html")  		
		http.ServeFile(w, r, idx)
	})

	// Health
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain")
		_, _ = w.Write([]byte("ok"))
	})


	// Simple JSON API
	mux.HandleFunc("/api/echo", func(w http.ResponseWriter, r *http.Request) {
		type Resp struct {
			Message string    `json:"message"`
			Time    time.Time `json:"time"`
		}
		q := r.URL.Query().Get("q")
		if q == "" {
			q = "hello"
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(Resp{Message: q, Time: time.Now()})
	})

    // Run a Python script from py_modules and return its JSON stdout
    mux.HandleFunc("/api/run_py", func(w http.ResponseWriter, r *http.Request) {
        name := r.URL.Query().Get("name") // script name without .py
        if name == "" {
            http.Error(w, "missing 'name' query param", http.StatusBadRequest)
            return
        }

        // Resolve py_modules folder next to static/templates
        root := filepath.Dir(filepath.Clean(staticDir))
        pyDir := filepath.Join(root, "py_modules")
        script := filepath.Join(pyDir, name+".py")

        if fi, err := os.Stat(script); err != nil || fi.IsDir() {
            http.Error(w, "script not found", http.StatusNotFound)
            return
        }

        // Optional args: ?arg=foo&arg=bar
        args := r.URL.Query()["arg"]

        // Choose Python executable (override with PYTHON_BIN)
        py := os.Getenv("PYTHON_BIN")
        if py == "" {
            if runtime.GOOS == "windows" {
                py = "python"
            } else {
                py = "python3"
            }
        }

        // Run with timeout
        ctx, cancel := context.WithTimeout(r.Context(), 15*time.Second)
        defer cancel()
        cmd := exec.CommandContext(ctx, py, append([]string{script}, args...)...)
        cmd.Dir = pyDir

        out, err := cmd.CombinedOutput()
        if ctx.Err() == context.DeadlineExceeded {
            http.Error(w, "script timed out", http.StatusGatewayTimeout)
            return
        }
        if err != nil {
            http.Error(w, fmt.Sprintf("script error: %v\n%s", err, string(out)), http.StatusBadGateway)
            return
        }

        // If stdout is valid JSON, return as-is; otherwise wrap it
        var js any
        if json.Unmarshal(out, &js) == nil {
            w.Header().Set("Content-Type", "application/json")
            w.Write(out)
            return
        }
        w.Header().Set("Content-Type", "application/json")
        _ = json.NewEncoder(w).Encode(map[string]any{
            "ok":     true,
            "output": string(out),
        })
    })

    return mux
}

//export StartServer
func StartServer(addr *C.char, staticPath *C.char) C.int {
	a := C.GoString(addr)
	p := C.GoString(staticPath)

	// Validate static dir exists
	if fi, err := os.Stat(p); err != nil || !fi.IsDir() {
		fmt.Println("invalid static dir:", p)
		return 2
	}

	srvMu.Lock()
	defer srvMu.Unlock()

	// If already running, do nothing
	if srv != nil {
		return 0
	}

	srv = &http.Server{
		Addr:              a,
		Handler:           buildMux(p),
		ReadTimeout:       10 * time.Second,
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	go func(s *http.Server) {
		_ = s.ListenAndServe()
	}(srv)

	return 0
}

//export StopServer
func StopServer() C.int {
	srvMu.Lock()
	s := srv
	srv = nil
	srvMu.Unlock()

	if s == nil {
		return 0
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := s.Shutdown(ctx); err != nil {
		fmt.Println("shutdown error:", err)
		return 1
	}
	return 0
}

func main() {}

'''

        elif self.lang == 'py':
            self.main_content = f'''
from {self.name} import server
import webbrowser

def main():
    webbrowser.open("http://127.0.0.1:8000")
    server.main()

if __name__ == "__main__":
    main()
'''
            self.stackscript_content = f'''
#!/bin/bash
apt-get update && apt-get upgrade
apt-get install python3 git
pip install -r requirements.txt
cp ./{self.name}/{self.name}.service /etc/systemd/system/
systemctl start {self.name}
systemctl enable {self.name}
'''

            self.service_content = f'''
# {self.name} Service.
[Unit]
Description={self.name} App
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/{self.name}/server.py
Type=simple
WorkingDirectory=/home/{self.name}
Restart=always

[Install]
WantedBy=default.target
'''
            
        self.files = {
            f'api/templates/index.html': self.index_content,
            f'api/static/go_wasm/go_wasm.go': self.go_wasm_content,
            f'api/static/go_wasm.js': self.go_wasm_js_content,
            f'api/static/worker.js': self.worker_content,
            }

        if self.lang == 'py':
            self.stackscript_content = f'''
#!/bin/bash
apt-get update && apt-get upgrade
apt-get install python3 git
cp ./{self.name}/{self.name}.service /etc/systemd/system/
systemctl start {self.name}
systemctl enable {self.name}
'''
            self.service_content = f'''
# {self.name} Service.
[Unit]
Description={self.name} App
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/{self.name}/api/server.py
Type=simple
WorkingDirectory=/home/{self.name}
Restart=always

[Install]
WantedBy=default.target
'''
            self.files[f'api/__init__.py'] = self.init_content
            self.files[f'api/__main__.py'] = self.main_content
            self.files[f'api/server.py'] = self.server_content
            self.folders.append(f'api/python_modules')
            self.files[f'api/python_modules/python_modules.py'] = self.python_modules_content
            self.folders.append(f'api/go_modules')
            self.files[f'api/go_modules/go_modules.go'] = self.go_modules_content
            self.files[f'api/stackscript.sh'] = self.stackscript_content
            self.files[f'api/{self.name}.service'] = self.service_content
        else:
            self.folders.append(f'api/py_modules')
            self.files[f'api/py_modules/hello.py'] = '''
import json
import sys

def main():
    args = sys.argv[1:]
    print(json.dumps({"ok": True, "args": args, "msg": "hello from python"}))

if __name__ == "__main__":
    main()
'''
            self.server_content = r'''

import subprocess, os, sys, platform, threading, asyncio, ctypes, time
import screeninfo
import websockets

shutdown_event = threading.Event()
active_lock = threading.Lock()
active_conns = 0  # number of open WS connections

def get_screen_size():
    try:
        m = screeninfo.get_monitors()[0]
        return m.width, m.height
    except Exception:
        return 1920, 1080

def get_platform_type():
    return platform.system()

def run_with_switches(system, url):
    import shutil
    wW, wH = 1024, 768
    sW, sH = get_screen_size()
    x = (sW - wW)//2
    y = (sH - wH)//2
    args = [
        f"--app={url}",
        "--disable-extensions",
        "--guest",
        f"--window-size={wW},{wH}",
        f"--window-position={x},{y}",
    ]
    # Windows direct
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
    import shutil, webbrowser
    binaries = ["google-chrome","chromium","chromium-browser","brave-browser","microsoft-edge"]
    for b in binaries:
        p = shutil.which(b)
        if p:
            subprocess.Popen([p]+args)
            return
    webbrowser.open(url)

def start_ws_server():
    async def handler(ws):
        global active_conns
        with active_lock:
            active_conns += 1
        try:
            await ws.wait_closed()
        finally:
            trigger = False
            with active_lock:
                active_conns -= 1
                if active_conns == 0:
                    trigger = True
            if trigger:
                shutdown_event.set()

    async def run():
        async with websockets.serve(handler, "127.0.0.1", 8765):
            while not shutdown_event.is_set():
                await asyncio.sleep(0.2)

    asyncio.run(run())

def start_shutdown_watcher(lib):
    def watcher():
        shutdown_event.wait()
        try:
            lib.StopServer()
        except:
            pass
        # small grace
        time.sleep(0.2)
        os._exit(0)
    threading.Thread(target=watcher, daemon=True).start()

# Go shared lib load (adjust names if needed)
libname = {
    "Linux": "server-linux.so",
    "Darwin": "server-darwin.so",
    "Windows": "server-windows.so",
}[platform.system()]
libpath = os.path.join(os.path.dirname(__file__), libname)
lib = ctypes.CDLL(libpath)
lib.StartServer.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.StartServer.restype = ctypes.c_int
lib.StopServer.argtypes = []
lib.StopServer.restype = ctypes.c_int

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))

def main():
    system = get_platform_type()
    # Start WS sidecar
    threading.Thread(target=start_ws_server, daemon=True).start()
    # Start watcher
    start_shutdown_watcher(lib)
    # Start Go server
    lib.StartServer(b":8080", STATIC_DIR.encode())
    # Launch browser (after slight delay so server starts)
    threading.Timer(0.3, lambda: run_with_switches(system, "http://127.0.0.1:8080")).start()
    # Block main thread until exit
    shutdown_event.wait()

if __name__ == "__main__":
    main()

'''
            
            self.stackscript_content = f'''
#!/bin/bash
apt-get update && apt-get upgrade
apt-get install go git
cp ./{self.name}/{self.name}.service /etc/systemd/system/
systemctl start {self.name}
systemctl enable {self.name}
'''
            self.service_content = f'''
# {self.name} Service.
[Unit]
Description={self.name} App
After=network.target

[Service]
ExecStart=/usr/bin/go /home/{self.name}/api/main
Type=simple
WorkingDirectory=/home/{self.name}
Restart=always

[Install]
WantedBy=default.target
'''
            self.files['api/server.py'] = self.server_content
            self.files[f'api/server.go'] = self.go_server_content
            self.files[f'api/stackscript.sh'] = self.stackscript_content
            self.files[f'api/{self.name}.service'] = self.service_content


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
            if not os.path.exists(folder):
                os.mkdir(folder)
                print(f'created "{folder}" folder.')
            else:
                click.echo(f'{Fore.RED}"{folder}" already exists.\nAborting...{Style.RESET_ALL}')
                return
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()

        os.chdir(f'api/static/go_wasm/')
        os.system(f'go mod init example/go_modules')
        os.chdir(f'../../')
        if self.lang == 'py':
            os.chdir(f'go_modules/')
            os.system(f'go mod init example/go_modules')
            os.chdir(f'../../')
        else:
            os.system(f'go mod init example/{self.name}')
            # os.system(f'go get github.com/gofiber/fiber/v2')
            # os.system(f'go mod tidy')
            os.chdir(f'../')
        # system = platform.system()

        # if system == 'Darwin':
        #     cmd = 'cp'
        # elif system == 'Linux':
        #     cmd = 'cp'
        # else:
        #     cmd = 'copy'

        # Get the directory of the current script
        current_directory = os.path.dirname(os.path.abspath(__file__))

        if self.lang == 'py':
            with open('api/requirements.txt', 'w') as f:
                f.write('''
annotated-types==0.7.0
anyio==4.10.0
certifi==2025.8.3
charset-normalizer==3.4.3
click==8.2.1
colorama==0.4.6
fastapi==0.116.1
h11==0.16.0
idna==3.10
pillow==11.3.0
pydantic==2.11.7
pydantic_core==2.33.2
requests==2.32.5
sniffio==1.3.1
starlette==0.47.3
typing-inspection==0.4.1
typing_extensions==4.14.1
urllib3==2.5.0
uvicorn==0.35.0
''')
        else:
            # shutil.copy(requirements_directory, f'desktop/requirements.txt')
            with open('api/requirements.txt', 'w') as f:
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

        logo_directory = os.path.join(os.path.dirname(current_directory), 'gupy_logo.png')       
        
        shutil.copy(logo_directory, f'api/static/logo/gupy_logo.png')

        splashscreen_directory = os.path.join(os.path.dirname(current_directory), 'gupy_splashscreen.png')       
        
        shutil.copy(splashscreen_directory, f'api/static/splashscreen/gupy_splashscreen.png')

        ico_directory = os.path.join(os.path.dirname(current_directory), 'gupy.ico')       
        
        shutil.copy(ico_directory, f'api/static/icon/gupy.ico')
        
        self.cythonize()
        self.gopherize()
        self.assemble()

    def run(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'
        if os.path.exists(f'server.py'):
            print(f'Building server.go file...')
            os.system(f'go build -o server-{platform.system().lower()}.so -buildmode=c-shared server.go ')


            # assign current python executable to use
            cmd = sys.executable.split(delim)[-1]
            os.system(f'{cmd} -m pip install -r requirements.txt')

            os.system(f'{cmd} server.py')
        # elif os.path.exists(f'server.go'):
        #     # os.chdir(f'api')
        #     os.system(f'go mod tidy')
        #     os.system(f'go run server.go')
        else:
            click.echo(f'{Fore.RED}Server file not found to run. Rename the main python entry file to server.py.{Style.RESET_ALL}')
            return
        
    # convert all py files to pyd extensions other than the __main__.py and __init__.py files
    def cythonize(self):
        if os.path.exists(f"api/python_modules") and os.path.exists(f"api/__main__.py"):
            os.chdir(f'api/python_modules')
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
            os.chdir('../../')


    # convert all go files to .c extensions other than ones in the go_wasm folder
    def gopherize(self):
        if os.path.exists(f"api/go_modules") and os.path.exists(f"api/server.py"):
            os.chdir(f'api/go_modules')
            os.system(f'go mod tidy')
            files = [f for f in glob.glob('*.go')]
            for file in files:
                print(f'Building {file} file...')
                try:
                  os.system(f'go build -o {os.path.splitext(file)[0]}.so -buildmode=c-shared {file} ')
                except Exception as e:
                  click.echo(f"{Fore.RED}Build failed.{Style.RESET_ALL}")
                  print(e)
            os.chdir('../../')



    # convert all go modules in the go_wasm folder to wasm
    def assemble(self):
        # Ensure wasm_exec.js is the one matching the local Go toolchain
        ensure_wasm_exec(dest_dir=os.path.join("api", "static", "go_wasm"))    
        os.chdir(f'api/static/go_wasm')
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
        os.chdir('../../../')

        # add assembly of cython modules

    def distribute(self, system, folder, delim, NAME, VERSION):
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
                    return            # creating version folder is doesnt already exist
            os.makedirs(f"{NAME}_{VERSION}", exist_ok=True)
            # shutil.rmtree(f"{VERSION}{delim}{folder}")
            # os.makedirs(VERSION, exist_ok=True)

            shutil.rmtree(f"{NAME}_{VERSION}")
            os.makedirs(f"{NAME}_{VERSION}", exist_ok=True)
            os.chdir('../')

            # Get the directory path to the current gupy.py file without the filename
            gupy_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(gupy_file_path)
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
                elif os.path.isdir(full_file_name) and file_name != NAME and file_name != 'dist' and file_name != 'venv' and file_name != 'virtualenv' and file_name != 'node_modules':
                    shutil.copytree(full_file_name, f"dist/{NAME}_{VERSION}/{file_name}", dirs_exist_ok=True)
                print('Copied '+file_name+' to '+f"dist/{NAME}_{VERSION}/{file_name}"+'...')
            if not os.path.exists(f'dist/{NAME}_{VERSION}/static/logo'):
                print('Creating logo directory...')
                logo_directory = os.path.join(gupy_file_path, 'gupy_logo.png')       
                print(logo_directory)
                os.makedirs(f'dist/{NAME}_{VERSION}/static', exist_ok=True)
                os.makedirs(f'dist/{NAME}_{VERSION}/static/logo', exist_ok=True)
                shutil.copy(logo_directory, f'dist/{NAME}_{VERSION}/static/logo/gupy_logo.png')
            if not os.path.exists(f'dist/{NAME}_{VERSION}/static/splashscreen'):
                print('Creating splashscreen directory...')
                splashscreen_directory = os.path.join(gupy_file_path, 'gupy_splashscreen.png')       
                os.makedirs(f'dist/{NAME}_{VERSION}/static', exist_ok=True)
                os.makedirs(f'dist/{NAME}_{VERSION}/static/splashscreen', exist_ok=True)
                shutil.copy(splashscreen_directory, f'dist/{NAME}_{VERSION}/static/splashscreen/gupy_splashscreen.png')
            if not os.path.exists(f'dist/{NAME}_{VERSION}/static/icon'):
                print('Creating icon directory...')
                ico_directory = os.path.join(gupy_file_path, 'gupy.ico')       
                os.makedirs(f'dist/{NAME}_{VERSION}/static', exist_ok=True)
                os.makedirs(f'dist/{NAME}_{VERSION}/static/icon', exist_ok=True)
                shutil.copy(ico_directory, f'dist/{NAME}_{VERSION}/static/icon/gupy.ico')
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
            ico_files = glob.glob(os.path.join('static/icon', '*.ico'))
            ico = ico_files[0].replace('\\','/')

            png_files = glob.glob(os.path.join('static/logo', '*.png'))
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

    # If the release is up-to-date, proceed to run the main server
    import server
    server.main()

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

            # if os.path.exists(f'server.go'):
                # # cythonize server.py
                # print(f'Building server.py file...')
                # os.system(f'cythonize -i server.py')
                # gopherize server.go
            try:
                print(f'Building server.go file...')
                os.system(f'go build -o server-{platform.system().lower()}.so -buildmode=c-shared server.go ')
                print(f'Files created successfully... \nNow compress the folder into a zip file and upload it to github releases (matching the zip filename in the release file; {NAME}_{VERSION}.zip). \nOptionally, you may install Inno Setup to create an installer with the {NAME}_{VERSION}_Setup.iss file.')
            except Exception as e:
                click.echo(f'{Fore.RED}Error: '+str(e)+f'.{Style.RESET_ALL}')
                return




        except Exception as e:
            click.echo(f'{Fore.RED}Error: '+str(e)+f'.{Style.RESET_ALL}')
            return
