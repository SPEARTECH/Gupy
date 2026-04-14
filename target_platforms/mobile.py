from . import base
import os
import platform
import subprocess
import shutil
import glob
import sys
from colorama import Fore, Style
import click

class Mobile(base.Base):
    index_content = '''
<!DOCTYPE html>
<html>
<head>
  <title>Gupy App</title>
  <link rel="manifest" href="./manifest.json">
  <script src="https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js"></script>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.7.2/dist/full.min.css" rel="stylesheet" type="text/css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/danfojs@1.1.2/lib/bundle.min.js"></script>
  <script src="https://code.highcharts.com/highcharts.js"></script>
  <script src="https://code.highcharts.com/modules/boost.js"></script>
  <script src="https://code.highcharts.com/modules/exporting.js"></script>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, minimal-ui">
    <link rel="icon" href="./static/icon/icon.png" type="image/png">
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
  <div id="app" style="text-align: center;">
    <center>
      <div class="h-full">
                <img class="mt-4 mask mask-squircle h-96 w-96 max-h-full max-w-full object-contain hover:-translate-y-2 ease-in-out transition" src="./static/logo/gupy_logo.png" />
        <br>
        <button class="btn bg-blue-500 border-blue-500 stroke-blue-500 hover:bg-blue-500 hover:border-blue-500 hover:shadow-md hover:shadow-blue-500/50 text-base-100 shadow-none transition-shadow">[[ message ]]</button>
        <br><br>
      </div>
    </center>
  </div>

  <script type="module">
    const { createApp } = Vue
    import { loadGoWasm } from './go_wasm.js';

    createApp({
      delimiters : ['[[', ']]'],
      data(){
        return {
          message: 'Welcome to Gupy!',
          data: {},
        }
      },
      async mounted() {
        try {
          const goExports = await loadGoWasm();
          console.log("Go WebAssembly add(5,7) =>", goExports.add(5, 7));
        } catch (error) {
          console.error("Error loading Go WASM:", error);
        }

        const worker = new Worker('worker.js');
        worker.postMessage({ message: '' });
        worker.onmessage = (message) => console.log(message.data);
      },
    }).mount('#app')
  </script>
</body>
</html>
'''

    worker_content = '''
onmessage = function(message){
    message.data['message'] = 'This is from the worker!'
    postMessage(message.data)
}
'''

    go_wasm_content = r'''
package main

import (
    "syscall/js"
    "fmt"
)

func add(this js.Value, args []js.Value) interface{} {
    a := args[0].Int()
    b := args[1].Int()
    sum := a + b
    fmt.Printf("Adding %d and %d to get %d\n", a, b, sum)
    return sum
}

func main() {
    fmt.Println("Go WebAssembly loaded and exposing functions.")
    js.Global().Set("add", js.FuncOf(add))
    select {}
}
'''

    def __init__(self, name):
        self.name = name

        self.manifest_content = '''
{
  "lang": "en-us",
  "name": "''' + self.name + '''",
  "short_name": "''' + self.name + '''",
  "description": "",
  "start_url": "/",
  "background_color": "#2f3d58",
  "theme_color": "#2f3d58",
  "orientation": "any",
  "display": "standalone",
  "icons": [
        { "src": "static/icon/icon.png", "type": "image/png", "sizes": "512x512" }
  ]
}
'''

        self.go_wasm_js_content = '''
export async function loadGoWasm() {
  await import('./go_wasm/wasm_exec.js');

  const go = new Go();
  const wasmURL = new URL('./go_wasm/go_wasm.wasm', import.meta.url);

  let result;
  try {
    result = await WebAssembly.instantiateStreaming(fetch(wasmURL), go.importObject);
  } catch (e) {
    const resp = await fetch(wasmURL);
    const buf = await resp.arrayBuffer();
    result = await WebAssembly.instantiate(buf, go.importObject);
  }

  go.run(result.instance);

  return {
    add: globalThis.add
  };
}
'''

        # Web assets live in mobile/web (so Capacitor can use webDir=web)
        self.folders = [
            'mobile',
            'mobile/resources',
            'mobile/web',
            'mobile/web/go_wasm',
            'mobile/web/static',
            'mobile/web/static/logo',
            'mobile/web/static/icon',
            'mobile/web/static/splashscreen',
        ]

        self.files = {
            'mobile/web/index.html': self.index_content,
            'mobile/web/manifest.json': self.manifest_content,
            'mobile/web/worker.js': self.worker_content,
            'mobile/web/go_wasm.js': self.go_wasm_js_content,
            'mobile/web/go_wasm/go_wasm.go': self.go_wasm_content,
            # wasm_exec.js is copied from GOROOT at create-time; do not embed it here
        }

    def _run_cmd(self, cmd, cwd=None, env=None, check=True):
        click.echo(f"{Fore.CYAN}$ {cmd}{Style.RESET_ALL}")
        return subprocess.run(cmd, shell=True, cwd=cwd, env=env, check=check)

    def _has_cmd(self, exe):
        return shutil.which(exe) is not None

    def _get_goroot(self):
        result = subprocess.run(["go", "env", "GOROOT"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Failed to get GOROOT: " + result.stderr)
        return result.stdout.strip()

    def _find_wasm_exec_js(self, goroot: str) -> str:
        """
        Go's wasm_exec.js has appeared in different locations across versions/distros.
        Try common known paths, then fall back to searching under GOROOT.
        """
        candidates = [
            os.path.join(goroot, "misc", "wasm", "wasm_exec.js"),
            os.path.join(goroot, "lib", "wasm", "wasm_exec.js"),
        ]
        for p in candidates:
            if os.path.isfile(p):
                return p

        # Fallback: search (keep it bounded to GOROOT)
        for root, _dirs, files in os.walk(goroot):
            if "wasm_exec.js" in files:
                return os.path.join(root, "wasm_exec.js")

        raise FileNotFoundError(
            "wasm_exec.js was not found under GOROOT.\n"
            f"GOROOT={goroot}\n"
            "Checked common paths:\n"
            + "\n".join(f"  - {c}" for c in candidates)
            + "\nIf this is a non-standard Go install, reinstall Go from https://go.dev/dl/ "
              "or ensure a full GOROOT is present."
        )

    def _setup_capacitor(self, project_root):
        # Requires node tooling
        if not (self._has_cmd("node") and self._has_cmd("npm") and self._has_cmd("npx")):
            click.echo(f"{Fore.YELLOW}Node/npm/npx not found. Skipping native wrapper creation.{Style.RESET_ALL}")
            click.echo("Install Node.js (includes npm), then re-run from the mobile folder.")
            return

        app_id = click.prompt("App ID (reverse-DNS)", default="com.example.gupyapp", show_default=True)
        create_android = click.confirm("Create Android wrapper (Capacitor)?", default=True)
        system = platform.system()
        create_ios = False
        if system == "Darwin":
            create_ios = click.confirm("Create iOS wrapper (Capacitor)?", default=True)
        else:
            click.echo(f"{Fore.YELLOW}iOS wrapper creation requires macOS. Skipping iOS.{Style.RESET_ALL}")

        # Initialize npm project if missing
        pkg_json = os.path.join(project_root, "package.json")
        if not os.path.exists(pkg_json):
            self._run_cmd("npm init -y", cwd=project_root)

        # Install capacitor deps
        self._run_cmd("npm i @capacitor/core", cwd=project_root)
        self._run_cmd("npm i -D @capacitor/cli", cwd=project_root)

        # cap init (idempotent-ish; will fail if already initialized)
        try:
            self._run_cmd(f'npx cap init "{self.name}" "{app_id}" --web-dir=web', cwd=project_root)
        except subprocess.CalledProcessError:
            click.echo(f"{Fore.YELLOW}Capacitor already initialized (or init failed). Continuing...{Style.RESET_ALL}")

        if create_android:
            try:
                self._run_cmd("npx cap add android", cwd=project_root)
            except subprocess.CalledProcessError:
                click.echo(f"{Fore.YELLOW}Android already added (or add failed). Continuing...{Style.RESET_ALL}")

        if create_ios:
            try:
                self._run_cmd("npx cap add ios", cwd=project_root)
            except subprocess.CalledProcessError:
                click.echo(f"{Fore.YELLOW}iOS already added (or add failed). Continuing...{Style.RESET_ALL}")

        # Generate native icons/splash from mobile/resources/icon.png and mobile/resources/splash.png
        # (Capacitor does NOT use web/static for native icons by default.)
        try:
            # Copy from web/static into resources to keep a single "source of truth" for the template.
            web_icon = os.path.join(project_root, "web", "static", "icon", "icon.png")
            web_splash = os.path.join(project_root, "web", "static", "splashscreen", "splash.png")
            res_icon = os.path.join(project_root, "resources", "icon.png")
            res_splash = os.path.join(project_root, "resources", "splash.png")
            if os.path.isfile(web_icon):
                shutil.copy(web_icon, res_icon)
            if os.path.isfile(web_splash):
                shutil.copy(web_splash, res_splash)

            self._run_cmd("npm i -D @capacitor/assets", cwd=project_root, check=False)
            icon_src = os.path.join(project_root, "resources", "icon.png")
            splash_src = os.path.join(project_root, "resources", "splash.png")
            if os.path.isfile(icon_src) and os.path.isfile(splash_src):
                self._run_cmd("npx @capacitor/assets generate", cwd=project_root, check=False)
            else:
                click.echo(
                    f"{Fore.YELLOW}Skipping native icon/splash generation (missing mobile/resources/icon.png or splash.png).{Style.RESET_ALL}"
                )
        except Exception:
            click.echo(f"{Fore.YELLOW}Skipping native icon/splash generation (@capacitor/assets).{Style.RESET_ALL}")

        # Sync web assets into native projects
        self._run_cmd("npx cap sync", cwd=project_root)

        click.echo(f"{Fore.GREEN}Mobile native wrappers ready.{Style.RESET_ALL}")
        click.echo("Next steps:")
        if create_android:
            click.echo(r"  Android build:  cd mobile && npx cap open android   (or)   cd mobile\android && gradlew assembleDebug")
        if create_ios:
            click.echo("  iOS build:      cd mobile && npx cap open ios      (or use xcodebuild on the generated workspace)")

    def create(self):
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
            os.makedirs(folder, exist_ok=True)
            print(f'created "{folder}" folder.')

        for file in self.files:
            with open(file, 'x', encoding='utf-8') as f:
                f.write(self.files.get(file))
            print(f'created "{file}" file.')

        # Copy default assets into web/static/* (continuity with other project types)
        current_directory = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_directory)
        logo_src = os.path.join(project_root, 'gupy_logo.png')
        splash_src = os.path.join(project_root, 'gupy_splashscreen.png')

        # web/static/logo
        shutil.copy(logo_src, 'mobile/web/static/logo/gupy_logo.png')
        # web/static/icon
        shutil.copy(logo_src, 'mobile/web/static/icon/icon.png')
        # web/static/splashscreen
        if os.path.isfile(splash_src):
            shutil.copy(splash_src, 'mobile/web/static/splashscreen/splash.png')

        # Keep the legacy location too (some older templates or user code may reference it)
        shutil.copy(logo_src, 'mobile/web/gupy_logo.png')

        # Capacitor native asset sources (used by `npx @capacitor/assets generate`)
        shutil.copy('mobile/web/static/icon/icon.png', 'mobile/resources/icon.png')
        if os.path.isfile('mobile/web/static/splashscreen/splash.png'):
            shutil.copy('mobile/web/static/splashscreen/splash.png', 'mobile/resources/splash.png')

        # build wasm + copy wasm_exec.js from GOROOT
        os.chdir('mobile/web/go_wasm')
        self._run_cmd('go mod init example/go_wasm', cwd=os.getcwd(), check=False)
        self._run_cmd('go mod tidy', cwd=os.getcwd(), check=False)

        # Copy wasm_exec.js from local Go installation (robust path detection)
        goroot = self._get_goroot()
        wasm_exec_src = self._find_wasm_exec_js(goroot)
        shutil.copy(wasm_exec_src, os.getcwd())

        os.chdir('../../../')
        self.assemble()
        # prompt to create native wrappers
        if click.confirm("Create native Android/iOS wrapper projects now (Capacitor)?", default=True):
            self._setup_capacitor(project_root=os.path.join(os.getcwd(), "mobile"))

    def run(self):
        # Simple preview server for the web assets
        os.chdir('mobile/web')
        cmd = sys.executable
        self._run_cmd(f'"{cmd}" -m http.server 8080', cwd=os.getcwd(), check=False)

    def assemble(self):
        # Rebuild all wasm in mobile/web/go_wasm
        os.chdir('mobile/web/go_wasm')

        self._run_cmd('go mod tidy', cwd=os.getcwd(), check=False)

        def build_wasm(filename):
            env = os.environ.copy()
            env['GOOS'] = 'js'
            env['GOARCH'] = 'wasm'
            out = f"{os.path.splitext(filename)[0]}.wasm"
            result = subprocess.run(f'go build -o {out}', shell=True, env=env)
            if result.returncode == 0:
                click.echo(f"{Fore.GREEN}Built {out}{Style.RESET_ALL}")
            else:
                click.echo(f"{Fore.RED}Build failed for {filename}{Style.RESET_ALL}")

        for filename in glob.glob('*.go'):
            build_wasm(filename)

        os.chdir('../../../')

        # If capacitor exists, sync updated web assets into native projects
        if os.path.exists(os.path.join('mobile', 'capacitor.config.json')) or os.path.exists(os.path.join('mobile', 'capacitor.config.ts')):
            if shutil.which("npx"):
                try:
                    # Keep resources in sync with web/static for icon & splash
                    web_icon = os.path.join('mobile', 'web', 'static', 'icon', 'icon.png')
                    web_splash = os.path.join('mobile', 'web', 'static', 'splashscreen', 'splash.png')
                    res_icon = os.path.join('mobile', 'resources', 'icon.png')
                    res_splash = os.path.join('mobile', 'resources', 'splash.png')
                    if os.path.isfile(web_icon):
                        os.makedirs(os.path.dirname(res_icon), exist_ok=True)
                        shutil.copy(web_icon, res_icon)
                    if os.path.isfile(web_splash):
                        os.makedirs(os.path.dirname(res_splash), exist_ok=True)
                        shutil.copy(web_splash, res_splash)

                    # Keep native icon/splash in sync if resources exist
                    if os.path.isfile(os.path.join('mobile', 'resources', 'icon.png')) and os.path.isfile(os.path.join('mobile', 'resources', 'splash.png')):
                        self._run_cmd("npx @capacitor/assets generate", cwd=os.path.join(os.getcwd(), "mobile"), check=False)
                    self._run_cmd("npx cap sync", cwd=os.path.join(os.getcwd(), "mobile"), check=False)
                except Exception:
                    pass