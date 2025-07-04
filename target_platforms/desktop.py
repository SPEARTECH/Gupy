from . import base
import os
import platform
import glob
import subprocess
import shutil
import sys
from colorama import Fore, Style
import click

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
  // Delay connection slightly to ensure the WS server is up
  setTimeout(() => {
    const host = location.hostname;
    const ws = new WebSocket(`ws://${host}:8765/`);
    ws.onopen = () => console.log("WS connected");
    ws.onclose = () => console.log("WS closed");
    ws.onerror = (e) => console.error("WS error", e);
    window.addEventListener('beforeunload', () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    });
  }, 500); // 500ms delay; adjust as needed

</script>
<script>
  // When the user is leaving, use sendBeacon to notify the server to shut down.
  window.addEventListener('beforeunload', () => {
    navigator.sendBeacon('/shutdown');
  });
</script>
  <script type="module">
    const { createApp } = Vue
     import { loadGoWasm } from '{{url_for('static', filename='go_wasm.js')}}';
    
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

          let worker = new Worker("{{url_for('static', filename='worker.js')}}");
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

    server_content = r'''


# Documentation:
#   https://flask.palletsprojects.com/en/3.0.x/

import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
from flask import Flask, render_template, render_template_string, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
# import numpy as np
import json
import platform
import screeninfo  # Install with `pip install screeninfo`
import threading
import asyncio
import websockets    # pip install websockets

app = Flask(__name__)

# a threading Event that we will set when the browser tab closes
shutdown_event = threading.Event()

async def _ws_handler(ws, path):
    try:
        # just keep this alive until the client closes
        await ws.recv()
    except websockets.exceptions.ConnectionClosed:
        pass
    shutdown_event.set()

def start_ws_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    srv = websockets.serve(_ws_handler, '127.0.0.1', 8765)
    loop.run_until_complete(srv)
    loop.run_forever()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return 'ok', 200

def get_screen_size():
    """Returns screen width and height."""
    try:
        screen = screeninfo.get_monitors()[0]  # Get primary monitor
        return screen.width, screen.height
    except Exception as e:
        print("Could not get screen resolution:", e)
        return 1920, 1080  # Default resolution if detection fails
    

# WORKSAFE=False
# try:
#     from gevent.pywsgi import WSGIServer
# except Exception as e:
#     print(e)
#     WORKSAFE=True
def get_platform_type():
    system = platform.system()
    return system

def run_with_switches(system, url):
    """Opens a Chromium-based browser at the center of the screen in incognito mode, with broad compatibility."""
    import shutil

    screen_width, screen_height = get_screen_size()
    window_width, window_height = 1024, 768
    pos_x = (screen_width - window_width) // 2
    pos_y = (screen_height - window_height) // 2

    common_args = [
        f"--app={url}",
        "--disable-pinch",
        "--disable-extensions",
        "--guest",
        "--incognito",
        f"--window-size={window_width},{window_height}",
        f"--window-position={pos_x},{pos_y}",
    ]

    # List of possible browser executables for each platform
    browser_candidates = []
    if system == 'Darwin':
        browser_candidates = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
            '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
            shutil.which('google-chrome'),
            shutil.which('chromium'),
            shutil.which('chromium-browser'),
            shutil.which('brave-browser'),
        ]
    elif system == 'Linux':
        browser_candidates = [
            shutil.which('google-chrome'),
            shutil.which('chromium'),
            shutil.which('chromium-browser'),
            shutil.which('brave-browser'),
            shutil.which('microsoft-edge'),
        ]
    else:
        # Windows handled as before
        if os.path.exists("C:/Program Files/Google/Chrome/Application/chrome.exe"):
            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
            command = [chrome_path] + common_args
            print("Running command:", command)
            subprocess.Popen(command)
            return
        elif os.path.exists("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"):
            chrome_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
            command = [chrome_path] + common_args
            print("Running command:", command)
            subprocess.Popen(command)
            return
        print("Chromium-based browser not found or default browser not set.")

        # Remove None values from browser_candidates
        browser_candidates = [b for b in browser_candidates if b]
    
    # Try each candidate and run the first one that exists
    for browser in browser_candidates:
        if browser and os.path.exists(browser):
            command = [browser] + common_args
            print("Running command:", command)
            subprocess.Popen(command)
            return

    # Fallback: try to open in default browser (may not support all switches)
    print("No supported Chromium-based browser found. Falling back to default browser.")
    import webbrowser
    try:
      webbrowser.open(url)
    except Exception as e:
      if platform.system() == 'Linux':
        # For Linux, use xdg-open
        os.system(f'xdg-open {url}')



def stop_previous_flask_server():
    try:
        # Read the PID from the file
        with open(f'{os.path.expanduser("~")}/flask_server.pid', 'r') as f:
          pid = int(f.read().strip())

        # Determine the system type
        system = platform.system()

        # Terminate the Flask server process based on the system type
        if system == "Windows":
          command = f'taskkill /F /PID {pid}'
        elif system == "Linux" or system == "Darwin":  # Darwin is macOS
          command = f'kill -9 {pid}'
        else:
          raise Exception(f"Unsupported system type: {system}")

        subprocess.run(command, shell=True, check=True)
        print("Previous Flask server process terminated.")
    except Exception as e:
        print(f"Error stopping previous Flask server: {e}")



# getting the name of the directory
# where the this file is present.
path = os.path.dirname(os.path.realpath(__file__))


# Routes
@app.route('/')
def index():
    # html = """
   
    # """

    # file_path = f'{os.path.dirname(os.path.realpath(__file__))}/templates/index.html'

    # with open(file_path, 'r') as file:
    #     html = ''
    #     for line in file:
    #         html += line
            
    #     return render_template_string(html)
        # return render('index.html')
        return render_template('index.html')

@app.route('/api/example_api_endpoint', methods=['GET'])
def example_api_endpoint():
    # Get the data from the request
    # data = request.json.get('data') # for POST requests with data

    #read from python/cython module
    from python_modules import python_modules

    py_message = python_modules.main()
    
    #read from go module
    from ctypes import cdll, c_char_p

    path = os.path.dirname(os.path.realpath(__file__))

    # Load the shared library
    try:
        go_modules = cdll.LoadLibrary(path+'/go_modules/go_modules.so')
    except Exception as e:
        print(str(e)+'\n Try running `python ./gupy.py gopherize -t <target_platform> -n <app_name>`')
        return

    # Define the return type of the function
    go_modules.go_module.restype = c_char_p
    
    go_message = go_modules.go_module().decode('utf-8')

    data = {'Python Module Message':py_message,'Go Module Message':go_message}

    # Perform data processing

    # Return the modified data as JSON
    return jsonify({'result': data})

def main():
    stop_previous_flask_server()

    pid_file = f'{os.path.expanduser("~")}/flask_server.pid'
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))  # Write the PID to the file

    # ADD SPLASH SCREEN?

    # Get current system type
    system = get_platform_type()

    threading.Thread(target=start_ws_server, daemon=True).start()

    # Run Apped Chrome Window
    run_with_switches(system)

    server_thread = threading.Thread(
        target=lambda: app.run(debug=True, threaded=True, port=8001, use_reloader=False),
        daemon=True
    )
    server_thread.start()

    # 4) block until WS drops
    shutdown_event.wait()

    # 5) hit shutdown endpoint
    try:
        requests.post('http://127.0.0.1:8001/shutdown')
    except:
        pass

    server_thread.join()

if __name__ == '__main__':
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

    worker_content = '''
onmessage = function(message){
    message.data['message'] = 'This is from the worker!'

    // console.log(message.data)

    postMessage(message.data)
}  

    '''


    go_wasm_content = r'''
// go_wasm/go_wasm.go
package main

import (
	"syscall/js"
	"fmt"
)

// add is a function that adds two integers passed from JavaScript.
func add(this js.Value, args []js.Value) interface{} {
	// Convert JS values to Go ints.
	a := args[0].Int()
	b := args[1].Int()
	sum := a + b
	fmt.Printf("Adding %d and %d to get %d\n", a, b, sum)
	return sum
}

func main() {
	fmt.Println("Go WebAssembly loaded and exposing functions.")

	// Register the add function on the global object.
	js.Global().Set("add", js.FuncOf(add))
	
	// Optionally, register more functions similarly:
	// js.Global().Set("multiply", js.FuncOf(multiply))

	// Prevent the Go program from exiting.
	select {}
}
    '''

    wasm_exec_content = r'''
// Copyright 2018 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

"use strict";

(() => {
const enosys = () => {
const err = new Error("not implemented");
err.code = "ENOSYS";
return err;
};

if (!globalThis.fs) {
let outputBuf = "";
globalThis.fs = {
constants: { O_WRONLY: -1, O_RDWR: -1, O_CREAT: -1, O_TRUNC: -1, O_APPEND: -1, O_EXCL: -1 }, // unused
writeSync(fd, buf) {
outputBuf += decoder.decode(buf);
const nl = outputBuf.lastIndexOf("\n");
if (nl != -1) {
console.log(outputBuf.substring(0, nl));
outputBuf = outputBuf.substring(nl + 1);
}
return buf.length;
},
write(fd, buf, offset, length, position, callback) {
if (offset !== 0 || length !== buf.length || position !== null) {
callback(enosys());
return;
}
const n = this.writeSync(fd, buf);
callback(null, n);
},
chmod(path, mode, callback) { callback(enosys()); },
chown(path, uid, gid, callback) { callback(enosys()); },
close(fd, callback) { callback(enosys()); },
fchmod(fd, mode, callback) { callback(enosys()); },
fchown(fd, uid, gid, callback) { callback(enosys()); },
fstat(fd, callback) { callback(enosys()); },
fsync(fd, callback) { callback(null); },
ftruncate(fd, length, callback) { callback(enosys()); },
lchown(path, uid, gid, callback) { callback(enosys()); },
link(path, link, callback) { callback(enosys()); },
lstat(path, callback) { callback(enosys()); },
mkdir(path, perm, callback) { callback(enosys()); },
open(path, flags, mode, callback) { callback(enosys()); },
read(fd, buffer, offset, length, position, callback) { callback(enosys()); },
readdir(path, callback) { callback(enosys()); },
readlink(path, callback) { callback(enosys()); },
rename(from, to, callback) { callback(enosys()); },
rmdir(path, callback) { callback(enosys()); },
stat(path, callback) { callback(enosys()); },
symlink(path, link, callback) { callback(enosys()); },
truncate(path, length, callback) { callback(enosys()); },
unlink(path, callback) { callback(enosys()); },
utimes(path, atime, mtime, callback) { callback(enosys()); },
};
}

if (!globalThis.process) {
globalThis.process = {
getuid() { return -1; },
getgid() { return -1; },
geteuid() { return -1; },
getegid() { return -1; },
getgroups() { throw enosys(); },
pid: -1,
ppid: -1,
umask() { throw enosys(); },
cwd() { throw enosys(); },
chdir() { throw enosys(); },
}
}

if (!globalThis.crypto) {
throw new Error("globalThis.crypto is not available, polyfill required (crypto.getRandomValues only)");
}

if (!globalThis.performance) {
throw new Error("globalThis.performance is not available, polyfill required (performance.now only)");
}

if (!globalThis.TextEncoder) {
throw new Error("globalThis.TextEncoder is not available, polyfill required");
}

if (!globalThis.TextDecoder) {
throw new Error("globalThis.TextDecoder is not available, polyfill required");
}

const encoder = new TextEncoder("utf-8");
const decoder = new TextDecoder("utf-8");

globalThis.Go = class {
constructor() {
this.argv = ["js"];
this.env = {};
this.exit = (code) => {
if (code !== 0) {
console.warn("exit code:", code);
}
};
this._exitPromise = new Promise((resolve) => {
this._resolveExitPromise = resolve;
});
this._pendingEvent = null;
this._scheduledTimeouts = new Map();
this._nextCallbackTimeoutID = 1;

const setInt64 = (addr, v) => {
this.mem.setUint32(addr + 0, v, true);
this.mem.setUint32(addr + 4, Math.floor(v / 4294967296), true);
}

const setInt32 = (addr, v) => {
this.mem.setUint32(addr + 0, v, true);
}

const getInt64 = (addr) => {
const low = this.mem.getUint32(addr + 0, true);
const high = this.mem.getInt32(addr + 4, true);
return low + high * 4294967296;
}

const loadValue = (addr) => {
const f = this.mem.getFloat64(addr, true);
if (f === 0) {
return undefined;
}
if (!isNaN(f)) {
return f;
}

const id = this.mem.getUint32(addr, true);
return this._values[id];
}

const storeValue = (addr, v) => {
const nanHead = 0x7FF80000;

if (typeof v === "number" && v !== 0) {
if (isNaN(v)) {
this.mem.setUint32(addr + 4, nanHead, true);
this.mem.setUint32(addr, 0, true);
return;
}
this.mem.setFloat64(addr, v, true);
return;
}

if (v === undefined) {
this.mem.setFloat64(addr, 0, true);
return;
}

let id = this._ids.get(v);
if (id === undefined) {
id = this._idPool.pop();
if (id === undefined) {
id = this._values.length;
}
this._values[id] = v;
this._goRefCounts[id] = 0;
this._ids.set(v, id);
}
this._goRefCounts[id]++;
let typeFlag = 0;
switch (typeof v) {
case "object":
if (v !== null) {
typeFlag = 1;
}
break;
case "string":
typeFlag = 2;
break;
case "symbol":
typeFlag = 3;
break;
case "function":
typeFlag = 4;
break;
}
this.mem.setUint32(addr + 4, nanHead | typeFlag, true);
this.mem.setUint32(addr, id, true);
}

const loadSlice = (addr) => {
const array = getInt64(addr + 0);
const len = getInt64(addr + 8);
return new Uint8Array(this._inst.exports.mem.buffer, array, len);
}

const loadSliceOfValues = (addr) => {
const array = getInt64(addr + 0);
const len = getInt64(addr + 8);
const a = new Array(len);
for (let i = 0; i < len; i++) {
a[i] = loadValue(array + i * 8);
}
return a;
}

const loadString = (addr) => {
const saddr = getInt64(addr + 0);
const len = getInt64(addr + 8);
return decoder.decode(new DataView(this._inst.exports.mem.buffer, saddr, len));
}

const timeOrigin = Date.now() - performance.now();
this.importObject = {
_gotest: {
add: (a, b) => a + b,
},
gojs: {
// Go's SP does not change as long as no Go code is running. Some operations (e.g. calls, getters and setters)
// may synchronously trigger a Go event handler. This makes Go code get executed in the middle of the imported
// function. A goroutine can switch to a new stack if the current stack is too small (see morestack function).
// This changes the SP, thus we have to update the SP used by the imported function.

// func wasmExit(code int32)
"runtime.wasmExit": (sp) => {
sp >>>= 0;
const code = this.mem.getInt32(sp + 8, true);
this.exited = true;
delete this._inst;
delete this._values;
delete this._goRefCounts;
delete this._ids;
delete this._idPool;
this.exit(code);
},

// func wasmWrite(fd uintptr, p unsafe.Pointer, n int32)
"runtime.wasmWrite": (sp) => {
sp >>>= 0;
const fd = getInt64(sp + 8);
const p = getInt64(sp + 16);
const n = this.mem.getInt32(sp + 24, true);
fs.writeSync(fd, new Uint8Array(this._inst.exports.mem.buffer, p, n));
},

// func resetMemoryDataView()
"runtime.resetMemoryDataView": (sp) => {
sp >>>= 0;
this.mem = new DataView(this._inst.exports.mem.buffer);
},

// func nanotime1() int64
"runtime.nanotime1": (sp) => {
sp >>>= 0;
setInt64(sp + 8, (timeOrigin + performance.now()) * 1000000);
},

// func walltime() (sec int64, nsec int32)
"runtime.walltime": (sp) => {
sp >>>= 0;
const msec = (new Date).getTime();
setInt64(sp + 8, msec / 1000);
this.mem.setInt32(sp + 16, (msec % 1000) * 1000000, true);
},

// func scheduleTimeoutEvent(delay int64) int32
"runtime.scheduleTimeoutEvent": (sp) => {
sp >>>= 0;
const id = this._nextCallbackTimeoutID;
this._nextCallbackTimeoutID++;
this._scheduledTimeouts.set(id, setTimeout(
() => {
this._resume();
while (this._scheduledTimeouts.has(id)) {
// for some reason Go failed to register the timeout event, log and try again
// (temporary workaround for https://github.com/golang/go/issues/28975)
console.warn("scheduleTimeoutEvent: missed timeout event");
this._resume();
}
},
getInt64(sp + 8),
));
this.mem.setInt32(sp + 16, id, true);
},

// func clearTimeoutEvent(id int32)
"runtime.clearTimeoutEvent": (sp) => {
sp >>>= 0;
const id = this.mem.getInt32(sp + 8, true);
clearTimeout(this._scheduledTimeouts.get(id));
this._scheduledTimeouts.delete(id);
},

// func getRandomData(r []byte)
"runtime.getRandomData": (sp) => {
sp >>>= 0;
crypto.getRandomValues(loadSlice(sp + 8));
},

// func finalizeRef(v ref)
"syscall/js.finalizeRef": (sp) => {
sp >>>= 0;
const id = this.mem.getUint32(sp + 8, true);
this._goRefCounts[id]--;
if (this._goRefCounts[id] === 0) {
const v = this._values[id];
this._values[id] = null;
this._ids.delete(v);
this._idPool.push(id);
}
},

// func stringVal(value string) ref
"syscall/js.stringVal": (sp) => {
sp >>>= 0;
storeValue(sp + 24, loadString(sp + 8));
},

// func valueGet(v ref, p string) ref
"syscall/js.valueGet": (sp) => {
sp >>>= 0;
const result = Reflect.get(loadValue(sp + 8), loadString(sp + 16));
sp = this._inst.exports.getsp() >>> 0; // see comment above
storeValue(sp + 32, result);
},

// func valueSet(v ref, p string, x ref)
"syscall/js.valueSet": (sp) => {
sp >>>= 0;
Reflect.set(loadValue(sp + 8), loadString(sp + 16), loadValue(sp + 32));
},

// func valueDelete(v ref, p string)
"syscall/js.valueDelete": (sp) => {
sp >>>= 0;
Reflect.deleteProperty(loadValue(sp + 8), loadString(sp + 16));
},

// func valueIndex(v ref, i int) ref
"syscall/js.valueIndex": (sp) => {
sp >>>= 0;
storeValue(sp + 24, Reflect.get(loadValue(sp + 8), getInt64(sp + 16)));
},

// valueSetIndex(v ref, i int, x ref)
"syscall/js.valueSetIndex": (sp) => {
sp >>>= 0;
Reflect.set(loadValue(sp + 8), getInt64(sp + 16), loadValue(sp + 24));
},

// func valueCall(v ref, m string, args []ref) (ref, bool)
"syscall/js.valueCall": (sp) => {
sp >>>= 0;
try {
const v = loadValue(sp + 8);
const m = Reflect.get(v, loadString(sp + 16));
const args = loadSliceOfValues(sp + 32);
const result = Reflect.apply(m, v, args);
sp = this._inst.exports.getsp() >>> 0; // see comment above
storeValue(sp + 56, result);
this.mem.setUint8(sp + 64, 1);
} catch (err) {
sp = this._inst.exports.getsp() >>> 0; // see comment above
storeValue(sp + 56, err);
this.mem.setUint8(sp + 64, 0);
}
},

// func valueInvoke(v ref, args []ref) (ref, bool)
"syscall/js.valueInvoke": (sp) => {
sp >>>= 0;
try {
const v = loadValue(sp + 8);
const args = loadSliceOfValues(sp + 16);
const result = Reflect.apply(v, undefined, args);
sp = this._inst.exports.getsp() >>> 0; // see comment above
storeValue(sp + 40, result);
this.mem.setUint8(sp + 48, 1);
} catch (err) {
sp = this._inst.exports.getsp() >>> 0; // see comment above
storeValue(sp + 40, err);
this.mem.setUint8(sp + 48, 0);
}
},

// func valueNew(v ref, args []ref) (ref, bool)
"syscall/js.valueNew": (sp) => {
sp >>>= 0;
try {
const v = loadValue(sp + 8);
const args = loadSliceOfValues(sp + 16);
const result = Reflect.construct(v, args);
sp = this._inst.exports.getsp() >>> 0; // see comment above
storeValue(sp + 40, result);
this.mem.setUint8(sp + 48, 1);
} catch (err) {
sp = this._inst.exports.getsp() >>> 0; // see comment above
storeValue(sp + 40, err);
this.mem.setUint8(sp + 48, 0);
}
},

// func valueLength(v ref) int
"syscall/js.valueLength": (sp) => {
sp >>>= 0;
setInt64(sp + 16, parseInt(loadValue(sp + 8).length));
},

// valuePrepareString(v ref) (ref, int)
"syscall/js.valuePrepareString": (sp) => {
sp >>>= 0;
const str = encoder.encode(String(loadValue(sp + 8)));
storeValue(sp + 16, str);
setInt64(sp + 24, str.length);
},

// valueLoadString(v ref, b []byte)
"syscall/js.valueLoadString": (sp) => {
sp >>>= 0;
const str = loadValue(sp + 8);
loadSlice(sp + 16).set(str);
},

// func valueInstanceOf(v ref, t ref) bool
"syscall/js.valueInstanceOf": (sp) => {
sp >>>= 0;
this.mem.setUint8(sp + 24, (loadValue(sp + 8) instanceof loadValue(sp + 16)) ? 1 : 0);
},

// func copyBytesToGo(dst []byte, src ref) (int, bool)
"syscall/js.copyBytesToGo": (sp) => {
sp >>>= 0;
const dst = loadSlice(sp + 8);
const src = loadValue(sp + 32);
if (!(src instanceof Uint8Array || src instanceof Uint8ClampedArray)) {
this.mem.setUint8(sp + 48, 0);
return;
}
const toCopy = src.subarray(0, dst.length);
dst.set(toCopy);
setInt64(sp + 40, toCopy.length);
this.mem.setUint8(sp + 48, 1);
},

// func copyBytesToJS(dst ref, src []byte) (int, bool)
"syscall/js.copyBytesToJS": (sp) => {
sp >>>= 0;
const dst = loadValue(sp + 8);
const src = loadSlice(sp + 16);
if (!(dst instanceof Uint8Array || dst instanceof Uint8ClampedArray)) {
this.mem.setUint8(sp + 48, 0);
return;
}
const toCopy = src.subarray(0, dst.length);
dst.set(toCopy);
setInt64(sp + 40, toCopy.length);
this.mem.setUint8(sp + 48, 1);
},

"debug": (value) => {
console.log(value);
},
}
};
}

async run(instance) {
if (!(instance instanceof WebAssembly.Instance)) {
throw new Error("Go.run: WebAssembly.Instance expected");
}
this._inst = instance;
this.mem = new DataView(this._inst.exports.mem.buffer);
this._values = [ // JS values that Go currently has references to, indexed by reference id
NaN,
0,
null,
true,
false,
globalThis,
this,
];
this._goRefCounts = new Array(this._values.length).fill(Infinity); // number of references that Go has to a JS value, indexed by reference id
this._ids = new Map([ // mapping from JS values to reference ids
[0, 1],
[null, 2],
[true, 3],
[false, 4],
[globalThis, 5],
[this, 6],
]);
this._idPool = [];   // unused ids that have been garbage collected
this.exited = false; // whether the Go program has exited

// Pass command line arguments and environment variables to WebAssembly by writing them to the linear memory.
let offset = 4096;

const strPtr = (str) => {
const ptr = offset;
const bytes = encoder.encode(str + "\0");
new Uint8Array(this.mem.buffer, offset, bytes.length).set(bytes);
offset += bytes.length;
if (offset % 8 !== 0) {
offset += 8 - (offset % 8);
}
return ptr;
};

const argc = this.argv.length;

const argvPtrs = [];
this.argv.forEach((arg) => {
argvPtrs.push(strPtr(arg));
});
argvPtrs.push(0);

const keys = Object.keys(this.env).sort();
keys.forEach((key) => {
argvPtrs.push(strPtr(`${key}=${this.env[key]}`));
});
argvPtrs.push(0);

const argv = offset;
argvPtrs.forEach((ptr) => {
this.mem.setUint32(offset, ptr, true);
this.mem.setUint32(offset + 4, 0, true);
offset += 8;
});

// The linker guarantees global data starts from at least wasmMinDataAddr.
// Keep in sync with cmd/link/internal/ld/data.go:wasmMinDataAddr.
const wasmMinDataAddr = 4096 + 8192;
if (offset >= wasmMinDataAddr) {
throw new Error("total length of command line and environment variables exceeds limit");
}

this._inst.exports.run(argc, argv);
if (this.exited) {
this._resolveExitPromise();
}
await this._exitPromise;
}

_resume() {
if (this.exited) {
throw new Error("Go program has already exited");
}
this._inst.exports.resume();
if (this.exited) {
this._resolveExitPromise();
}
}

_makeFuncWrapper(id) {
const go = this;
return function () {
const event = { id: id, this: this, args: arguments };
go._pendingEvent = event;
go._resume();
return event.result;
};
}
}
})();
    '''

    read_me = ''' 

    '''
    
    init_content = '''
import sys
import os
# Add the parent directory of 'target_platforms' to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))'''

    def __init__(self, name, lang=''):
        self.name = name
        self.lang = lang
        self.folders = [
          f'desktop', 
          f'desktop/templates',
          f'desktop/static',
          f'desktop/static/go_wasm',
          # f'{self.name}/desktop/dev/templates/python_wasm',
        ]
        self.go_wasm_js_content = '''
// go_wasm.js
// This function initializes the Go WASM module and returns an object with exported functions.
export async function loadGoWasm() {
  // Dynamically import wasm_exec.js. (Make sure it’s included in your package.)
  await import('./go_wasm/wasm_exec.js');

  // Create a new Go instance.
  const go = new Go();

  // Construct an absolute URL for the WASM file relative to this module.
  const wasmURL = new URL('./go_wasm/go_wasm.wasm', import.meta.url);

  // Use instantiateStreaming with a fallback to ArrayBuffer.
  let result;
  try {
    result = await WebAssembly.instantiateStreaming(fetch(wasmURL), go.importObject);
  } catch (streamingError) {
    console.warn("instantiateStreaming failed, falling back:", streamingError);
    const response = await fetch(wasmURL);
    const buffer = await response.arrayBuffer();
    result = await WebAssembly.instantiate(buffer, go.importObject);
  }

  // Run the Go WebAssembly module. Note that go.run is asynchronous,
  // but it blocks further execution until the Go code stops.
  // In our case, the Go code never exits (because of select{}), but that’s fine.
  go.run(result.instance);

  // At this point, the Go code has registered its functions on the global object.
  // Return an object with references to the exported functions.
  return {
    add: globalThis.add
    // Add other exported functions here if needed.
  };
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
  <link rel="icon" href="/static/gupy_logo.png" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle h-96 hover:-translate-y-2 ease-in-out transition" src="/static/gupy_logo.png" />
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
    // Watchdog WS on Go /ws endpoint
    const ws = new WebSocket(`ws://${location.host}/ws`);
    window.addEventListener('beforeunload', () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    });
</script>

  <script type="module">
    const { createApp } = Vue
     import { loadGoWasm } from './static/go_wasm.js';
    
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
  <link rel="icon" href="/static/gupy_logo.png" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  </head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
        <img class="mt-4 mask mask-squircle h-96 hover:-translate-y-2 ease-in-out transition" src="/static/gupy_logo.png" />
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
            self.server_content = r'''

'''
        elif self.lang == 'py':
            self.main_content = f'''
from {self.name} import server

def main():
    server.main()

if __name__ == "__main__":
    main()
'''

        self.files = {
            f'desktop/templates/index.html': self.index_content,
            f'desktop/static/go_wasm/go_wasm.go': self.go_wasm_content,
            f'desktop/static/go_wasm/wasm_exec.js': self.wasm_exec_content,
            f'desktop/static/go_wasm.js': self.go_wasm_js_content,
            f'desktop/static/worker.js': self.worker_content,
            }

        if self.lang == 'py':
            self.files[f'desktop/__init__.py'] = self.init_content
            self.files[f'desktop/__main__.py'] = self.main_content
            self.files[f'desktop/server.py'] = self.server_content
            self.folders.append(f'desktop/python_modules')
            self.files[f'desktop/python_modules/python_modules.py'] = self.python_modules_content
            self.folders.append(f'desktop/go_modules')
            self.files[f'desktop/go_modules/go_modules.go'] = self.go_modules_content
        else:
            self.files[f'desktop/main.go'] = self.server_content

    def create(self):
        if 'desktop/main.go' in self.files:
            print("Please enter Github information for the app where your release package will be uploaded...")
            REPO_OWNER = input(f'Enter the Github repository owner: ')
            REPO_NAME = input("Enter the Github repository name: ")

            self.server_content = r'''
package main

import (
    "context"
    "fmt"
    "log"
    "net/http"
    "os"
    "os/exec"
    "os/signal"
    "path/filepath"
    "runtime"
    "syscall"
    "time"
    "unsafe"

    "github.com/gorilla/websocket"
    "golang.org/x/sys/windows"
)

var shutdownCh = make(chan struct{})

var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin:     func(r *http.Request) bool { return true },
}

func main() {
    // Check for updates before starting the server
	repoOwner := "'''+REPO_OWNER+r'''" // Replace with your GitHub repo owner
    repoName := "'''+REPO_NAME+r'''"   // Replace with your GitHub repo name
    if !checkForUpdates(repoOwner, repoName) {
        return
    }

    srv := &http.Server{
        Addr:    ":8080",
        Handler: routes(),
    }

    // open Chrome in app mode (incognito, centered)
    go openChrome("http://127.0.0.1:8080")

    // run server
    go func() {
        log.Println("Listening on http://127.0.0.1:8080")
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("ListenAndServe(): %v", err)
        }
    }()

    // wait for OS signal or WS‐triggered shutdown
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
    select {
    case <-quit:
    case <-shutdownCh:
        log.Println("Browser closed, shutting down…")
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    if err := srv.Shutdown(ctx); err != nil {
        log.Fatalf("Server Shutdown: %v", err)
    }
    log.Println("Server stopped gracefully")
}

func checkForUpdates(repoOwner, repoName string) bool {
    // Fetch the latest release from GitHub
    latestRelease, err := fetchLatestRelease(repoOwner, repoName)
    if err != nil {
        fmt.Println("Error fetching latest release:", err)
        return true // Proceed with the current version
    }

    // Read the current release version from the release file
    currentRelease, err := readCurrentRelease()
    if err != nil {
        fmt.Println("Error reading current release:", err)
        return true // Proceed with the current version
    }

    // Compare the versions
    if latestRelease != currentRelease {
        fmt.Printf("New release available: %s. Updating...\n", latestRelease)

        // Determine the platform and run the appropriate install script
        system := runtime.GOOS
        var installScript string
        if system == "windows" {
            installScript = "install.bat"
        } else {
            installScript = "install.sh"
        }

        cmd := exec.Command(installScript)
        cmd.Stdout = os.Stdout
        cmd.Stderr = os.Stderr
        if err := cmd.Run(); err != nil {
            fmt.Println("Error running install script:", err)
            return true // Proceed with the current version
        }

        // Exit after running the installer
        return false
    }

    fmt.Println("Current release is up to date.")
    return true
}

func fetchLatestRelease(repoOwner, repoName string) (string, error) {
    apiURL := fmt.Sprintf("https://api.github.com/repos/%s/%s/releases/latest", repoOwner, repoName)
    resp, err := http.Get(apiURL)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return "", fmt.Errorf("failed to fetch release: %s", resp.Status)
    }

    var release GitHubRelease
    if err := json.NewDecoder(resp.Body).Decode(&release); err != nil {
        return "", err
    }

    return release.Name, nil
}

func readCurrentRelease() (string, error) {
    releaseFile := filepath.Join(filepath.Dir(os.Args[0]), "release")
    data, err := ioutil.ReadFile(releaseFile)
    if err != nil {
        return "", err
    }
    return string(data), nil
}

func routes() http.Handler {
    mux := http.NewServeMux()
    mux.HandleFunc("/", rootHandler)
    mux.HandleFunc("/ws", wsHandler)
    return mux
}

// copy your wsHandler & rootHandler here...
func rootHandler(w http.ResponseWriter, r *http.Request) {
    // serve your SPA entrypoint (adjust path as needed)
    http.ServeFile(w, r, filepath.Join("templates", "index.html"))
}

func wsHandler(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        fmt.Println("WS upgrade failed:", err)
        return
    }
    defer conn.Close()

    // block until client disconnects
    for {
        if _, _, err := conn.ReadMessage(); err != nil {
            // signal main to shutdown
            close(shutdownCh)
            return
        }
    }
}

// GetScreenSize retrieves the screen dimensions on Windows
func GetScreenSize() (int, int) {
    var info windows.Rect
    user32 := windows.NewLazySystemDLL("user32.dll")
    getClientRect := user32.NewProc("GetClientRect")
    getDesktop := user32.NewProc("GetDesktopWindow")

    hwnd, _, _ := getDesktop.Call()
    getClientRect.Call(hwnd, uintptr(unsafe.Pointer(&info)))

    return int(info.Right - info.Left), int(info.Bottom - info.Top)
}

// FindBrowserPath locates a Chromium‐based browser on any OS
func FindBrowserPath() string {
    var candidates []string
    switch runtime.GOOS {
    case "windows":
        candidates = []string{
            `C:\Program Files\Google\Chrome\Application\chrome.exe`,
            `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`,
            `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`,
        }
    case "darwin":
        candidates = []string{
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        }
    default:
        candidates = []string{
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        }
    }
    for _, path := range candidates {
        if _, err := os.Stat(path); err == nil {
            return path
        }
    }
    return ""
}

// openChrome launches Chrome in “app” mode, centered & incognito
func openChrome(url string) {
    browser := FindBrowserPath()
    if browser == "" {
        fmt.Println("No Chromium-based browser found. Falling back to the default browser.")
        openDefaultBrowser(url)
        return
    }

    sw, sh := GetScreenSize()
    ww, wh := 1024, 768
    x := (sw - ww) / 2
    y := (sh - wh) / 2

    args := []string{
        "--app=" + url,
        "--disable-pinch",
        "--disable-extensions",
        "--guest",
        "--incognito",
        fmt.Sprintf("--window-size=%d,%d", ww, wh),
        fmt.Sprintf("--window-position=%d,%d", x, y),
    }

    cmd := exec.Command(browser, args...)
    if err := cmd.Start(); err != nil {
        fmt.Println("failed to launch browser:", err)
    }
}

// openDefaultBrowser opens the URL in the system's default web browser
func openDefaultBrowser(url string) {
    var cmd *exec.Cmd

    switch runtime.GOOS {
    case "windows":
        cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
    case "darwin":
        cmd = exec.Command("open", url)
    default: // Linux and other Unix-like systems
        cmd = exec.Command("xdg-open", url)
    }

    if err := cmd.Start(); err != nil {
        fmt.Println("Failed to open the default browser:", err)
    }
}

'''
            self.files[f'desktop/main.go'] = self.server_content
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
            f = open(file, 'x', encoding='utf-8')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()

        os.chdir(f'desktop/static/go_wasm/')
        os.system(f'go mod init example/go_modules')
        os.chdir(f'../../')
        if self.lang == 'py':
            os.chdir(f'go_modules/')
            os.system(f'go mod init example/go_modules')
            os.chdir(f'../../')
        else:
            os.system(f'go mod init example/{self.name}')
            os.system(f'go get github.com/gorilla/websocket')
            os.system(f'go get golang.org/x/sys/windows')

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
            # Construct the path to the target file
            # requirements_directory = os.path.join(os.path.dirname(current_directory), 'requirements.txt')       
            
            # shutil.copy(requirements_directory, f'desktop/requirements.txt')
            with open('desktop/requirements.txt', 'w') as f:
                f.write('''
blinker==1.9.0
click==8.1.8
colorama==0.4.6
Flask==3.1.0
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
screeninfo==0.8.1
Werkzeug==3.1.3
''')

        logo_directory = os.path.join(os.path.dirname(current_directory), 'gupy_logo.png')       
        
        shutil.copy(logo_directory, f'desktop/static/gupy_logo.png')

        ico_directory = os.path.join(os.path.dirname(current_directory), 'gupy.ico')       
        
        shutil.copy(ico_directory, f'desktop/static/gupy.ico')
        
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
            # assign current python executable to use
            cmd = sys.executable.split(delim)[-1]

            os.system(f'{cmd} server.py')
        elif os.path.exists(f'main.go'):
            # os.chdir(f'desktop')
            os.system(f'go mod tidy')
            os.system(f'go run main.go')
        else:
            click.echo(f'{Fore.RED}Server file not found to run. Rename the main entry file to server.py or server.go.{Style.RESET_ALL}')
            return
    # convert all py files to pyd extensions other than the __main__.py and __init__.py files
    def cythonize(self):
        if os.path.exists(f"desktop/python_modules") and os.path.exists(f"desktop/__main__.py"):
            os.chdir(f'desktop/python_modules')
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
        if os.path.exists(f"desktop/go_modules") and os.path.exists(f"desktop/server.py"):
            os.chdir(f'desktop/go_modules')
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
        os.chdir(f'desktop/static/go_wasm')
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

            # creating version folder is doesnt already exist
            os.makedirs(f"{NAME}_{VERSION}", exist_ok=True)
            # shutil.rmtree(f"{VERSION}{delim}{folder}")
            # os.makedirs(VERSION, exist_ok=True)

            shutil.rmtree(f"{NAME}_{VERSION}")
            os.makedirs(f"{NAME}_{VERSION}", exist_ok=True)
            os.chdir('../')

            # Get the directory path to the current gupy.py file without the filename
            gupy_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            if os.path.exists('server.py'):
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
                    elif os.path.isdir(full_file_name) and file_name != NAME and file_name != 'dist' and file_name != 'venv' and file_name != 'virtualenv':
                        shutil.copytree(full_file_name, f"dist/{NAME}_{VERSION}/{file_name}", dirs_exist_ok=True)
                    print('Copied '+file_name+' to '+f"dist/{NAME}_{VERSION}/{file_name}"+'...')
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
                ico_files = glob.glob(os.path.join('static', '*.ico'))
                ico = ico_files[0]

                png_files = glob.glob(os.path.join('static', '*.png'))
                png = png_files[0].replace('\\','/') # changing to forward slashes for mac/linux compatibility

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

    # If the release is up-to-date, proceed to run the main server
    import server
    server.main()

if __name__ == "__main__":
    main()
                        '''
                bash_install_script_content = r'''
#!/bin/bash

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
Terminal=false
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
echo desktopShortcut.TargetPath = "%~dp0python/windows/pythonw.exe" >> CreateShortcut.vbs
echo desktopShortcut.Arguments = "run.py" >> CreateShortcut.vbs
echo desktopShortcut.WorkingDirectory = "%cd%" >> CreateShortcut.vbs
echo desktopShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo desktopShortcut.Save >> CreateShortcut.vbs
echo Set dirShortcut = objShell.CreateShortcut("%cd%\\'''+ NAME +r'''.lnk") >> CreateShortcut.vbs
echo dirShortcut.TargetPath = "%~dp0python/windows/pythonw.exe" >> CreateShortcut.vbs
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

                print(f'Files created successfully... \nNow compress the folder into a zip file and upload it to github releases (matching the zip filename in the release file; {NAME}_{VERSION}.zip). \nOptionally, you may install Inno Setup to create an installer with the {NAME}_{VERSION}_Setup.iss file.')

            elif os.path.exists('main.go'):
                # move files+folders into project folder if just created
                comp_file_ext = 'so' #go only gopherized file extension - no pyd should be present in go desktop app

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

                def get_goroot():
                    # Run 'go env GOROOT' command and capture the output
                    result = subprocess.run(["go", "env", "GOROOT"], capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout.strip()  # Remove any surrounding whitespace/newlines
                    else:
                        raise Exception("Failed to get GOROOT: " + result.stderr)

                # copy go folder contents into go/ folder
                def get_golang_install_location():
                    goroot = get_goroot()

                    if goroot:
                        return goroot
                    else:
                        return "GOROOT environment variable is not set."

                golang_location = get_golang_install_location()
                print(f"Golang is installed at: {golang_location}")

                os.makedirs(f"dist/{NAME}_{VERSION}/go", exist_ok=True)
                shutil.copytree(golang_location, f"dist/{NAME}_{VERSION}/go", dirs_exist_ok=True)
                print('Copied go folder...')
                # create run.go and go.mod for starting entry script for current os
                os.chdir(f'dist/{NAME}_{VERSION}')
                

                # if system == 'win':
                #     subprocess.run(f'.\\go\\bin\\go.exe mod init example.com/{NAME}', shell=True, check=True)
                # else:
                #     subprocess.run(f'./go/bin/go mod init example.com/{NAME}', shell=True, check=True)
                # subprocess.run(f'.\\go\\bin\\go.exe mod tidy', shell=True, check=True)
                # Use glob to find all .ico files in the folder
                ico_files = glob.glob(os.path.join('static', '*.ico'))
                ico = ico_files[0]
                png_files = glob.glob(os.path.join('static', '*.png'))
                png = png_files[0].replace('\\','/') # changing to forward slashes for mac/linux compatibility

                print("Please enter Github information for the app where your release package will be uploaded...")
                REPO_OWNER = input(f'Enter the Github repository owner: ')
                REPO_NAME = input("Enter the Github repository name: ")

                bash_install_script_content = r'''
#!/bin/bash

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

# Set the working directory to the script's directory
cd "$(dirname "$0")"
echo "Current directory is: $(pwd)"

# Determine the OS and current directory
OS=$(uname)
CURRENT_DIR=$(pwd)

if [ "$OS" = "Darwin" ]; then
    # macOS: create a minimal AppleScript-based app that launches run.py
    APP_PATH="$HOME/Desktop/'''+NAME+r'''.app"
    echo "Creating macOS desktop shortcut at $APP_PATH"
    
    sudo chmod +x go/bin/go
    echo "Building main.go for macOS..."
    go/bin/go build main.go 
    sudo chmod +x main
    mkdir -p "$APP_PATH/Contents/MacOS"
    cat <<EOF > "$APP_PATH/Contents/MacOS/'''+NAME+r'''"
#!/bin/bash
# Change directory to the folder containing run.py
cd "$CURRENT_DIR"
./main

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
    echo "Building main.go for Linux..."
    sudo chmod +x go/bin/go
    go/bin/go build main.go 
    sudo chmod +x main
    DESKTOP_FILE="$HOME/Desktop/'''+NAME+r'''.desktop"
    echo "Creating Linux desktop shortcut at $DESKTOP_FILE"
    cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name='''+NAME+r'''
Comment=Run '''+NAME+r'''
Exec=$CURRENT_DIR/main
Icon=$CURRENT_DIR/'''+png+r'''
Terminal=false
Type=Application
Categories=Utility;
EOF
    chmod +x "$DESKTOP_FILE"
    echo "Application updated. Now launch the app from the desktop shortcut!"
else
    echo "Unsupported OS: $OS"
    exit 1
fi
        '''





                bat_install_script_content = r'''
@echo off
setlocal enabledelayedexpansion

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
    :: Delete all files in the folder except install.bat
    echo Deleting old files except install.bat...
    for %%f in (*) do (
        if /I not "%%f"=="install.bat" (
            del /q "%%f"
        )
    )
    echo Old files deleted.

    :: Delete all folders in the current directory
    echo Deleting old folders...
    for /d %%d in (*) do (
        rd /s /q "%%d"
    )
    for /d %%d in (*) do (
        rd /s /q "%%d"
    )
    echo Old files and folders deleted.
    
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


:: Create VBScript to make a desktop shortcut to run "python run.py"
echo Creating desktop shortcut...
echo Set objShell = CreateObject("WScript.Shell") > CreateShortcut.vbs
echo Set desktopShortcut = objShell.CreateShortcut(objShell.SpecialFolders("Desktop") ^& "\\'''+ NAME +r'''.lnk") >> CreateShortcut.vbs
echo desktopShortcut.TargetPath = "%~dp0main.exe" >> CreateShortcut.vbs
echo desktopShortcut.WorkingDirectory = "%cd%" >> CreateShortcut.vbs
echo desktopShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo desktopShortcut.Save >> CreateShortcut.vbs
echo Set dirShortcut = objShell.CreateShortcut("%cd%\\'''+ NAME +r'''.lnk") >> CreateShortcut.vbs
echo dirShortcut.TargetPath = "%~dp0main.exe" >> CreateShortcut.vbs
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
    ; Filename: "{app}\main.exe"; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\{#Icon}"; IconIndex: 0

; Shortcut in the application folder
; Name: "{app}\{#AppName}.lnk"; \
    ; Filename: "{app}\main.exe"; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\{#Icon}"; IconIndex: 0

;[Run]
; Optionally launch the app after install
;Filename: "{app}\main.exe"; \
;    WorkingDir: "{app}"; \
;    Flags: nowait postinstall skipifsilent
[Run]
; Run install.bat after copying files
Filename: "{app}\install.bat"; \
Description: "Finalize installation"; \
WorkingDir: "{app}"; \
Flags: shellexec postinstall waituntilterminated skipifsilent
                '''
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

                print(f'Files created successfully... \nNow compress the folder into a zip file and upload it to github releases (matching the zip filename in the release file; {NAME}_{VERSION}.zip). \nOptionally, you may install Inno Setup to create an installer with the {NAME}_{VERSION}_Setup.iss file.')

        except Exception as e:
            print('Error: '+str(e))
            return
