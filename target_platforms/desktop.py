from . import base
import os
import platform
import glob
import subprocess

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
<!-- <script>
  // Disable right-clicking
document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});
</script> -->
<script src="{{url_for('static', filename='go_wasm/wasm_exec.js')}}"></script>

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
        mounted() {
          const go = new Go();
          WebAssembly.instantiateStreaming(fetch("{{url_for('static', filename='go_wasm/go_wasm.wasm')}}"), go.importObject).then((result) => {
            go.run(result.instance);
          });

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

    server_content = '''

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

# WORKSAFE=False
# try:
#     from gevent.pywsgi import WSGIServer
# except Exception as e:
#     print(e)
#     WORKSAFE=True
def get_platform_type():
    system = platform.system()
    return system

def run_with_switches(system):
    # Check the default browser
    if system == 'Darwin':
        # Path for Google Chrome on macOS
        chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        if os.path.exists(chrome_path):
            command = [
                chrome_path,
                '--app=http://127.0.0.1:8001/',
                '--disable-pinch',
                '--disable-extensions',
                '--guest'
            ]
        print("Running command:", command)
        subprocess.Popen(command)
        return
    elif system == 'Linux':
        # Typical command for launching Google Chrome on Linux
        chrome_path = '/usr/bin/google-chrome'
        if os.path.exists(chrome_path):
            command = [
                chrome_path,
                '--app=http://127.0.0.1:8001/',
                '--disable-pinch',
                '--disable-extensions',
                '--guest'
            ]
        else:
            # Fallback to chromium if google-chrome is not installed
            chromium_path = '/usr/bin/chromium-browser'
            if os.path.exists(chromium_path):
                command = [
                    chromium_path,
                    '--app=http://127.0.0.1:8001/',
                    '--disable-pinch',
                    '--disable-extensions',
                    '--guest'
                ]
        print("Running command:", command)
        subprocess.Popen(command)
        return
    else:
        if os.path.exists("C:/Program Files/Google/Chrome/Application/chrome.exe"):
            command = [
                "C:/Program Files/Google/Chrome/Application/chrome.exe",
                '--app=http://127.0.0.1:8001/',
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
                '--app=http://127.0.0.1:8001/',
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

    # Get current system type
    system = get_platform_type()

    # Run Apped Chrome Window
    run_with_switches(system)

    # if WORKSAFE == False:
    #     http_server = WSGIServer(("127.0.0.1", 8000), app)
    #     http_server.serve_forever()
    # else:
    app.run(debug=True, threaded=True, port=8001, use_reloader=False)

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

    worker_content = '''
onmessage = function(message){
    message.data['message'] = 'This is from the worker!'

    // console.log(message.data)

    postMessage(message.data)
}  

    '''


    go_wasm_content = '''
package main

import "fmt"

func main() {
	fmt.Println("Hello, from Go WebAssembly!")
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
            f'desktop/templates/index.html': self.index_content,
            f'desktop/static/go_wasm/go_wasm.go': self.go_wasm_content,
            f'desktop/static/go_wasm/wasm_exec.js': self.wasm_exec_content,
            f'desktop/static/worker.js': self.worker_content,
            }

        if self.lang == 'py':
            self.files[f'desktop/server.py'] = self.server_content
            self.folders.append(f'desktop/python_modules')
            self.files[f'desktop/python_modules/python_modules.py'] = self.python_modules_content
            self.folders.append(f'desktop/go_modules')
            self.files[f'desktop/go_modules/go_modules.go'] = self.go_modules_content
        else:
            self.files[f'desktop/server.go'] = self.server_content

    def create(self):
        # check if platform project already exists, if so, prompt the user
        if self.folders[0] in os.listdir('.'):
            while True:
                userselection = input(self.folders[0]' already exists for the app '+ self.name +'. Would you like to overwrite the existing '+ self.folders[0]+' project? (y/n): ')
                if userselection.lower() == 'y':
                    userselection = input('Are you sure you want to recreate the '+ self.folders[0]+' project for '+ self.name +'? (y/n)')
                    if userselection.lower() == 'y':
                        print("Removing old version of project...")
                        os.system(f'rm -r "{self.folders[0]}"')
                        print("Continuing app platform creation.")
                        break
                    elif userselection.lower() != 'n':
                        print('Invalid input, please type y or n then press enter...')
                        continue
                    else:
                        print('Aborting app platform creation.')
                        return
                elif userselection.lower() != 'n':
                    print('Invalid input, please type y or n then press enter...')
                    continue
                else:
                    print('Aborting app platform creation.')
                    return
                    
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

        os.chdir(f'desktop/static/go_wasm/')
        os.system(f'go mod init example/go_modules')
        os.chdir(f'../')
        if self.lang == 'py':
            os.chdir(f'go_modules/')
            os.system(f'go mod init example/go_modules')
        else:
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
        os.chdir(f'cd ../../../')
        shutil.copy('gupy_logo.png', f'desktop/static/gupy_logo.png')
        self.cythonize()
        self.gopherize()
        self.assemble()

    def run(self):
        if os.path.exists(f'desktop/server.py'):
            # add check here for platform type and language 
            system = platform.system()

            if system == 'Darwin':
                cmd = 'python3'
            elif system == 'Linux':
                cmd = 'python'
            else:
                cmd = 'python'

            os.system(f'{cmd} desktop/server.py')
        else:
            os.chdir(f'desktop')
            os.system(f'go mod tidy')
            os.system(f'go run server.go')

    # convert all py files to pyd extensions other than the __main__.py and __init__.py files
    def cythonize(self):
        if os.path.exists(f"desktop/python_modules") and os.path.exists(f"desktop/server.py"):
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
        if os.path.exists(f"desktop/go_modules") and os.path.exists(f"desktop/dev/server.py"):
            os.chdir(f'desktop/go_modules')
            os.system(f'go mod tidy')
            files = [f for f in glob.glob('*.go')]
            for file in files:
                print(f'Building {file} file...')
                os.system(f'go build -o {os.path.splitext(file)[0]}.so -buildmode=c-shared {file} ')
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
              print("Build successful.")
          else:
              print("Build failed.")
        files = [f for f in glob.glob('*.go')]
        for filename in files:
          build_wasm(filename)
        os.chdir('../../../')

        # add assembly of cython modules

    # add packaging app to whl for pip install
    def package(self):
        pass
