from . import base
import os
import platform
import glob
import re
import subprocess
import shutil

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
        <img class="mt-4 mask mask-squircle h-96 hover:-translate-y-2 ease-in-out transition" src="{% static 'gupy_logo.png' %}" />
        <br>
        <button class="btn bg-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/50 text-base-100">[[ message ]] </button>
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
<script src="{% static 'go_wasm/wasm_exec.js' %}"></script>
  <script>
    const { createApp } = Vue
    
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
            axios.get('http://127.0.0.1:8000/api_endpoint')
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
          WebAssembly.instantiateStreaming(fetch("{% static 'go_wasm/go_wasm.wasm' %}"), go.importObject).then((result) => {
            go.run(result.instance);
          });

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
    path('api_endpoint/', views.api_endpoint, name='api_endpoint'),
    ]    
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

    def __init__(self, name):
        self.name = name
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

# Create your views here.
def index(request):
'''+r'''
    context = {}
    return render(request, 'index.html', context)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def api_endpoint(request):
    response = {'data':'success'}
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
            f'website/{self.name}/{self.name}_app/static/go_wasm/go_wasm.go': self.go_wasm_content,
            f'website/{self.name}/{self.name}_app/static/go_wasm/wasm_exec.js': self.wasm_exec_content,
            }

    def create(self):
      import shutil
      system = platform.system()

      if system == 'Darwin':
          cmd = 'python3'
      elif system == 'Linux':
          cmd = 'python'
      else:
          cmd = 'python'

      # check if platform project already exists, if so, prompt the user
      if self.folders[0] in os.listdir('.'):
          while True:
              userselection = input(self.folders[0]+' already exists for the app '+ self.name +'. Would you like to overwrite the existing '+ self.folders[0]+' project? (y/n): ')
              if userselection.lower() == 'y':
                  userselection = input('Are you sure you want to recreate the '+ self.folders[0]+' project for '+ self.name +'? (y/n)')
                  if userselection.lower() == 'y':
                      print("Removing old version of project...")
                      shutil.rmtree(os.path.join(os.getcwd(), self.folders[0]))
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
          os.mkdir(folder)
          print(f'created "{folder}" folder.')
      print('starting django project...')
      os.system('echo changing directory...')
      os.chdir(f'website/') #go into newly created folder
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
      import shutil
      os.mkdir(f'static/css')
      os.chdir('../../../')
      # Get the directory of the current script
      current_directory = os.path.dirname(os.path.abspath(__file__))

      # Construct the path to the target file
      logo_directory = os.path.join(os.path.dirname(current_directory), 'gupy_logo.png')       
      
      shutil.copy(logo_directory, f'website/{self.name}/{self.name}_app/static/gupy_logo.png')

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


    def run(self):
        if os.path.exists(f'website/{name}/manage.py'):
            # add check here for platform type and language 
            system = platform.system()

            if system == 'Darwin':
                cmd = 'python3'
            elif system == 'Linux':
                cmd = 'python'
            else:
                cmd = 'python'
            os.system(f'{cmd} website/{name}/manage.py runserver')
        # else:
        #     os.chdir(f'gupy_apps/{name}/desktop/dev')
        #     os.system(f'go mod tidy')
        #     os.system(f'go run server.go')


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
        print(os.getcwd())

    def assemble(self):
        # print(os.getcwd())
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
              print("Build successful.")
          else:
              print("Build failed.")
        files = [f for f in glob.glob('*.go')]
        for filename in files:
          build_wasm(filename)
        os.chdir('../../../../../')

        # add assembly of cython modules
