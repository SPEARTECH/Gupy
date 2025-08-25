from . import base
import os
import shutil
import platform
import sys
from colorama import Fore, Style
import click
import subprocess
import glob

class Script(base.Base):
    script_content = '''
def main():
    print('Script run complete.')

if __name__ == '__main__':
    main()
    
'''

    def __init__(self, name, lang='go'):
        self.name = name
        self.lang = lang
        self.init_content = f'''
import sys
import os
# Add the parent directory of 'target_platforms' to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .{self.name} import *
'''


        self.folders = [
            f'script',
            #   f'gupy_apps/{self.name}/cli/dev/python_modules',
            #   f'gupy_apps/{self.name}/cli/dev/cython_modules',
          ]
        if self.lang == 'py':
            self.main_content = f'''
from {self.name} import {self.name}

def main():
    {self.name}.main()

if __name__ == "__main__":
    main()
'''
            self.files = {
                f'script/__init__.py': self.init_content,
                f'script/__main__.py': self.main_content,
                f'script/{self.name}.py': self.script_content,
                }
        else:
            self.script_content = '''
package main

import (
    "fmt"
)

func main(){
    fmt.Println("Script run complete.")
}
            '''
            self.files = {
                f'script/main.go': self.script_content,
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

        if self.lang == 'py':
            with open('script/requirements.txt', 'w') as f:
                f.write('''
certifi==2025.8.3
charset-normalizer==3.4.3
idna==3.10
pillow==11.3.0
requests==2.32.5
urllib3==2.5.0
''')
        else:
            os.chdir('script')
            os.system(f'go mod init example/{self.name}')

        # logo_directory = os.path.join(os.path.dirname(current_directory), 'gupy_logo.png')       
        
        # shutil.copy(logo_directory, f'api/static/logo/gupy_logo.png')

        # splashscreen_directory = os.path.join(os.path.dirname(current_directory), 'gupy_splashscreen.png')       
        
        # shutil.copy(splashscreen_directory, f'api/static/splashscreen/gupy_splashscreen.png')

        # ico_directory = os.path.join(os.path.dirname(current_directory), 'gupy.ico')       
        
        # shutil.copy(ico_directory, f'api/static/icon/gupy.ico')


    def run(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'
        if os.path.exists(f'{self.name}.py'):
            # assign current python executable to use
            cmd = sys.executable.split(delim)[-1]
            os.system(f'{cmd} -m pip install -r requirements.txt')

            # os.system(f'{cmd} {name}/desktop/dev/server/server.py')
            os.system(f'{cmd} {self.name}.py')
        elif os.path.exists(f'main.go'):
            os.system(f'go run main.go')
        else:
            click.echo(f'{Fore.RED}No entry file found of "{self.name}.py" or "main.go"{Style.RESET_ALL}')
        
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
            git_selection = input(f'Do you intend to upload this release to Github for automatic updates? (y/n): ')
            if git_selection.lower() == 'y':
                print("Please enter Github information for the app where your release package will be uploaded...")
                REPO_OWNER = input(f'Enter the Github repository owner: ')
                REPO_NAME = input("Enter the Github repository name: ")
            
            if os.path.exists(f'{NAME}.py'):
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
                if not os.path.exists(f'dist/{NAME}_{VERSION}/static/logo'):
                    print('Creating logo directory...')
                    logo_directory = os.path.join(gupy_file_path, 'gupy_logo.png')       
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
                # gupy_framework_windows_deps.add_deps(f"dist/{NAME}{VERSION}/python")
                # gupy_framework_linux_deps.add_deps(f"dist/{NAME}{VERSION}/python")
                # gupy_framework_macos_deps.add_deps(f"dist/{NAME}{VERSION}/python/macos")
                # mac_pkg_file = gupy_framework_macos_deps.get_deps()[0]
                import py7zr
                archive_path = gupy_file_path + delim + 'python.7z'
                with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                    archive.extractall(path=f"dist/{NAME}_{VERSION}")
                # shutil.copytree(python_loc, f"dist/{NAME}{VERSION}/python", dirs_exist_ok=True)
                
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
    import '''+f'''{self.name}
    {self.name}.main()'''+r'''

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
Icon=$CURRENT_DIR/static/logo/'''+png+r'''
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




cd /d "%~dp0"

REM Create Desktop and local shortcuts via PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p=(Get-Location).Path; " ^
  "$py=Join-Path $p 'python\windows\python.exe'; " ^
  "$script=Join-Path $p 'run.py'; " ^
  "$ico=Join-Path $p '''+"'"+ico+"'"+r'''; " ^
  "$sh=New-Object -ComObject WScript.Shell; " ^
  "$desk=[Environment]::GetFolderPath('Desktop'); " ^
  "$s=$sh.CreateShortcut((Join-Path $desk'''+ " '"+NAME+r'''.lnk')); " ^
  "$s.TargetPath=$env:ComSpec; $s.Arguments='/K ""'+$py+'"" ""'+$script+'""'; " ^
  "$s.WorkingDirectory=$p; $s.IconLocation=$ico+',0'; $s.WindowStyle=1; $s.Save(); " ^
  "$s=$sh.CreateShortcut((Join-Path $p'''+ " '"+NAME+r'''.lnk')); " ^
  "$s.TargetPath=$env:ComSpec; $s.Arguments='/K ""'+$py+'"" ""'+$script+'""'; " ^
  "$s.WorkingDirectory=$p; $s.IconLocation=$ico+',0'; $s.WindowStyle=1; $s.Save()"


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
    ; Filename: "{app}\python\windows\python.exe"; \
    ; Parameters: """{app}\run.py"""; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\icon\{#Icon}"; IconIndex: 0

; Shortcut in the application folder
; Name: "{app}\{#AppName}.lnk"; \
    ; Filename: "{app}\python\windows\python.exe"; \
    ; Parameters: """{app}\run.py"""; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\icon\{#Icon}"; IconIndex: 0

;[Run]
; Optionally launch the app after install
;Filename: "{app}\python\windows\python.exe"; \
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
                        if comp_file_ext in file_name.split('.')[-1] and system in file_name:
                            shutil.copy(full_file_name, f"{NAME}/{VERSION}/{folder}")
                        elif comp_file_ext in file_name.split('.')[-1] and system in file_name:
                            shutil.copy(full_file_name, f"{NAME}/{VERSION}/{folder}")
                        elif file_name.split('.')[-1] != 'pyd' and file_name.split('.')[-1] != 'so':
                            shutil.copy(full_file_name, f"{NAME}/{VERSION}/{folder}")
                    elif os.path.isdir(full_file_name) and file_name != NAME and file_name != 'dist':
                        shutil.copytree(full_file_name, f"{NAME}/{VERSION}/{folder}/{file_name}", dirs_exist_ok=True)
                    print('Copied '+file_name+' to '+f"{NAME}/{VERSION}/{folder}/{file_name}"+'...')
                if not os.path.exists(f'dist/{NAME}_{VERSION}/static/logo'):
                    print('Creating logo directory...')
                    logo_directory = os.path.join(os.path.dirname(gupy_file_path), 'gupy_logo.png')       
                    os.makedirs(f'dist/{NAME}_{VERSION}/static', exist_ok=True)
                    os.makedirs(f'dist/{NAME}_{VERSION}/static/logo', exist_ok=True)
                    shutil.copy(logo_directory, f'dist/{NAME}_{VERSION}/static/logo/gupy_logo.png')
                if not os.path.exists(f'dist/{NAME}_{VERSION}/static/splashscreen'):
                    print('Creating splashscreen directory...')
                    splashscreen_directory = os.path.join(os.path.dirname(gupy_file_path), 'gupy_splashscreen.png')       
                    os.makedirs(f'dist/{NAME}_{VERSION}/static', exist_ok=True)
                    os.makedirs(f'dist/{NAME}_{VERSION}/static/splashscreen', exist_ok=True)
                    shutil.copy(splashscreen_directory, f'dist/{NAME}_{VERSION}/static/splashscreen/gupy_splashscreen.png')
                if not os.path.exists(f'dist/{NAME}_{VERSION}/static/icon'):
                    print('Creating icon directory...')
                    ico_directory = os.path.join(os.path.dirname(gupy_file_path), 'gupy.ico')       
                    os.makedirs(f'dist/{NAME}_{VERSION}/static', exist_ok=True)
                    os.makedirs(f'dist/{NAME}_{VERSION}/static/icon', exist_ok=True)
                    shutil.copy(ico_directory, f'dist/{NAME}_{VERSION}/static/icon/gupy.ico')

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

                os.makedirs(f"{NAME}/{VERSION}/{folder}/go", exist_ok=True)
                shutil.copytree(golang_location, f"{NAME}/{VERSION}/{folder}/go", dirs_exist_ok=True)
                print('Copied go folder...')
                # create run.go and go.mod for starting entry script for current os
                os.chdir(f"{NAME}/{VERSION}/{folder}")
                # if system == 'win':
                #     subprocess.run(f'.\\go\\bin\\go.exe mod init example.com/{NAME}', shell=True, check=True)
                # else:
                #     subprocess.run(f'./go/bin/go mod init example.com/{NAME}', shell=True, check=True)
                # subprocess.run(f'.\\go\\bin\\go.exe mod tidy', shell=True, check=True)
                # Use glob to find all .ico files in the folder
                ico_files = glob.glob(os.path.join('static/icon', '*.ico'))
                ico = ico_files[0].replace('\\','/') 

                png_files = glob.glob(os.path.join('static/logo', '*.png'))
                png = png_files[0].replace('\\','/') # changing to forward slashes for mac/linux compatibility


                # create install.bat/sh for compiling run.go
                NAME = NAME.replace('dist_', '')
                if folder == 'linux':
                    install_script_content = r'''
#!/bin/bash
'''
                    if git_selection.lower() == 'y':
                        install_script_content += r'''
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
                    install_script_content += r'''
# Navigate to the script's directory
cd "$(dirname "$0")"
sudo chmod -R 755 .

echo "Adding go to PATH..."
export PATH=$PATH:/usr/local/go/bin
echo "Compiling main.go..."
./go/bin/go build main.go

if [ $? -ne 0 ]; then
    echo "Go build failed. Exiting..."
    exit 1
fi

echo "Creating application shortcut..."
# Define paths for the icon and the target executable
ICON_PATH="$PWD/static/icon/'''+ ico +r'''"
TARGET_PATH="$PWD/main"

# Create the .desktop shortcut for the desktop
DESKTOP_SHORTCUT="$HOME/Desktop/'''+NAME+r'''.desktop"
cat > "$DESKTOP_SHORTCUT" <<EOL
[Desktop Entry]
Version=1.0
Name='''+NAME+r'''
Comment='''+NAME+r''' Application
Exec=$TARGET_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Application;
EOL

# Make the desktop shortcut executable
chmod +x "$DESKTOP_SHORTCUT"

# Create the .desktop shortcut in the application directory
DIR_SHORTCUT="$TARGET_PATH.desktop"
cat > "$DIR_SHORTCUT" <<EOL
[Desktop Entry]
Version=1.0
Name='''+NAME+r'''
Comment='''+NAME+r''' Application
Exec=$TARGET_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Application;
EOL

# Make the directory shortcut executable
chmod +x "$DIR_SHORTCUT"

echo "Shortcuts created successfully!"
'''
                    with open('install.sh', 'w') as f:
                        f.write(install_script_content)
                elif folder == 'mac':
                    install_script_content = r'''
#!/bin/bash
'''
                    if git_selection.lower() == 'y':
                        install_script_content += r'''
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
                    install_script_content += r'''
# Navigate to the script's directory
cd "$(dirname "$0")"
cd ..
sudo chmod -R 755 mac
cd mac

echo "Adding go to PATH..."
export PATH=$PATH:/usr/local/go/bin

echo "Compiling main.go..."
go/bin/go build main.go

if [ $? -ne 0 ]; then
    echo "Go build failed. Exiting..."
    exit 1
fi

# need to add desktop shortcut functionality to mac install script - 10-26-24

'''
                    with open('install.sh', 'w') as f:
                        f.write(install_script_content)
                else:
                    install_script_content = r'''
@echo off
setlocal enabledelayedexpansion
'''
                    if git_selection.lower() == 'y':
                        install_script_content += r'''
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
                    install_script_content += r'''
cd /d "%~dp0"

%~dp0go/bin/go.exe build main.go

if %errorlevel% neq 0 (
    echo Go build failed. Exiting...
    exit /b 1
)

echo Creating application shortcut...
REM Create a VBScript to make a desktop shortcut with an icon
echo Set objShell = CreateObject("WScript.Shell") > CreateShortcut.vbs
echo Set desktopShortcut = objShell.CreateShortcut(objShell.SpecialFolders("Desktop") ^& "\\'''+NAME+r'''.lnk") >> CreateShortcut.vbs
echo desktopShortcut.TargetPath = "%cd%\main.exe" >> CreateShortcut.vbs
echo desktopShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo desktopShortcut.Save >> CreateShortcut.vbs

REM Create a shortcut in the same directory as main.exe
echo Set dirShortcut = objShell.CreateShortcut("%cd%\\'''+NAME+r'''.lnk") >> CreateShortcut.vbs
echo dirShortcut.TargetPath = "%cd%\main.exe" >> CreateShortcut.vbs
echo dirShortcut.IconLocation = "%~dp0static/icon/'''+ ico +r'''" >> CreateShortcut.vbs
echo dirShortcut.Save >> CreateShortcut.vbs

REM Run the VBScript to create the shortcuts
cscript CreateShortcut.vbs

REM Clean up the VBScript file
del CreateShortcut.vbs

echo Shortcuts created successfully!
pause
'''     

                    with open('install.bat', 'w') as f:
                        f.write(install_script_content)
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
    ; Filename: "{app}\python\windows\python.exe"; \
    ; Parameters: """{app}\run.py"""; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\icon\{#Icon}"; IconIndex: 0

; Shortcut in the application folder
; Name: "{app}\{#AppName}.lnk"; \
    ; Filename: "{app}\python\windows\python.exe"; \
    ; Parameters: """{app}\run.py"""; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\icon\{#Icon}"; IconIndex: 0

;[Run]
; Optionally launch the app after install
;Filename: "{app}\python\windows\python.exe"; \
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
                        
                with open(NAME+'_'+VERSION+'_Setup.iss', 'w', newline='\n') as f:
                    f.write(iss_contents)
                print(f'Files created successfully... \nNow compress the folder into a zip file and upload it to github releases (matching the zip filename in the release file; {NAME}_{VERSION}.zip). \nOptionally, you may install Inno Setup to create an installer with the {NAME}_{VERSION}_Setup.iss file.')
        except Exception as e:
            print('Error: '+str(e))
            return



