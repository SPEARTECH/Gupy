from . import base
import os
import shutil
import platform
import sys
from colorama import Fore, Style
import click

class CLI(base.Base):
    index_content = '''
# Documentation: 
# https://click.palletsprojects.com/en/8.1.x/

from logging import exception
import click
import sys
import os

STRING = ''
CHOICE = ''

@click.group()
def cli():
    \'''
Example CLI tool
    \'''
    ##Running checks on python version
    version = '.'.join(sys.version.split(' ')[0].split('.')[:2])
    if float(version) < 3.0:
        raise Exception('Please use Python3+. Make sure you have created a virtual environment.')

@click.command(help='Runs CLI tool')
@click.option(
    '--string',
    '-s',
    required=True,
    help='String to return'
    )

@click.option(
    '--choice-list',
    '-c',
    type=click.Choice(
        ['1', '2', '3'], 
        case_sensitive=False
        ),
    multiple=True, 
    default=['1'], 
    help="Select numbers you would like to return (ie. -c 1 -c 2 -c 3)"
    )
def run(string,choice_list):
    STRING=string
    CHOICE=choice_list
    print('String entered = '+ STRING)
    print('Choices entered =')
    for choice in choice_list:
      print(choice)

def main():
    cli.add_command(run) #Add command for cli
    cli() #Run cli

if __name__ == '__main__':
    main()



'''

    init_content = '''
import sys
import os
# Add the parent directory of 'target_platforms' to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))'''

    def __init__(self, name, lang=''):
        self.name = name
        self.lang = lang
        if self.lang == 'py':
            self.main_content = f'''
from {self.name} import {self.name}

def main():
    {self.name}.main()

if __name__ == "__main__":
    main()
'''
        else:
            self.main_content = r'''
package main

import (
	"fmt"
	"os"
	"strconv"

	"github.com/spf13/cobra"
)

// Root command (base command `'''+self.name+r'''`)
var rootCmd = &cobra.Command{
	Use:   "'''+self.name+r'''",
	Short: "'''+self.name+r''' CLI - A simple command-line tool",
	Long:  "'''+self.name+r''' is a CLI application that provides useful commands such as greeting users and performing math operations.",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Welcome to '''+self.name+r''' CLI! Use `'''+self.name+r''' --help` to see available commands.")
	},
}

// `greet` command
var greetCmd = &cobra.Command{
	Use:   "greet",
	Short: "Greet a user",
	Long:  "This command greets the user with a friendly message.",
	Run: func(cmd *cobra.Command, args []string) {
		name, _ := cmd.Flags().GetString("name")
		if name == "" {
			name = "Guest"
		}
		fmt.Printf("Hello, %s! Welcome to '''+self.name+r''' CLI.\n", name)
	},
}

// `math` command (parent command)
var mathCmd = &cobra.Command{
	Use:   "math",
	Short: "Perform mathematical operations",
	Long:  "This command allows you to perform simple math operations such as addition.",
}

// `math add` command
var addCmd = &cobra.Command{
	Use:   "add [num1] [num2]",
	Short: "Add two numbers",
	Long:  "This command takes two numbers as arguments and returns their sum.",
	Args:  cobra.ExactArgs(2), // Ensure exactly 2 arguments
	Run: func(cmd *cobra.Command, args []string) {
		num1, err1 := strconv.Atoi(args[0])
		num2, err2 := strconv.Atoi(args[1])

		if err1 != nil || err2 != nil {
			fmt.Println("Error: Please provide two valid numbers.")
			return
		}

		fmt.Printf("The sum of %d and %d is %d\n", num1, num2, num1+num2)
	},
}

// Initialize the CLI
func init() {
	// Add `greet` command
	rootCmd.AddCommand(greetCmd)

	// Add `math` command group
	rootCmd.AddCommand(mathCmd)
	mathCmd.AddCommand(addCmd)

	// Add a flag to `greet` command
	greetCmd.Flags().StringP("name", "n", "", "Your name")
}

// Entry point
func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
'''

        self.folders = [
          f'cli',
        #   f'gupy_apps/{self.name}/cli/dev/python_modules',
        #   f'gupy_apps/{self.name}/cli/dev/cython_modules',
          ]
        if self.lang == 'py':
            self.files = {
                f'cli/__init__.py': self.init_content,
                f'cli/__main__.py': self.main_content,
                f'cli/{self.name}.py': self.index_content,
                }
        else:
            self.files = {
                f'cli/main.go': self.main_content,
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
            # Get the directory of the current script
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Construct the path to the target file
            requirements_directory = os.path.join(os.path.dirname(current_directory), 'requirements.txt')       
            
            shutil.copy(requirements_directory, f'cli/requirements.txt')
        else:
            os.chdir('cli')
            os.system(f'go mod init {self.name}')
            os.system('go get -u github.com/spf13/cobra@latest')
            os.system('go get -u github.com/spf13/cobra/cobra@latest')

    def run(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'
        if self.lang == 'py':
            # assign current python executable to use
            cmd = sys.executable.split(delim)[-1]

            # os.system(f'{cmd} {name}/desktop/dev/server/server.py')
            os.system(f'{cmd} {self.name}.py')
        else:
            os.system('go run main.go')

    def distribute(self, system, folder, VERSION):
        try:

            # creating project folder if doesnt already exist
            os.makedirs('dist', exist_ok=True)
            os.chdir('dist')

            # creating version folder is doesnt already exist
            os.makedirs(f"{NAME}{VERSION}", exist_ok=True)
            # shutil.rmtree(f"{VERSION}{delim}{folder}")
            # os.makedirs(VERSION, exist_ok=True)

            shutil.rmtree(f"{NAME}{VERSION}")
            os.makedirs(f"{NAME}{VERSION}", exist_ok=True)
            os.chdir('../')

            # Get the directory path to the current gupy.py file without the filename
            gupy_file_path = os.path.dirname(os.path.abspath(__file__))
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
                        shutil.copy(full_file_name, f"dist/{NAME}{VERSION}")
                    elif os.path.isdir(full_file_name) and file_name != NAME and file_name != 'dist' and file_name != 'venv' and file_name != 'virtualenv':
                        shutil.copytree(full_file_name, f"dist/{NAME}{VERSION}/{file_name}", dirs_exist_ok=True)
                    print('Copied '+file_name+' to '+f"dist/{NAME}{VERSION}/{file_name}"+'...')
                # package latest python if not selected - make python folder with windows/mac/linux
                os.makedirs(f"dist/{NAME}{VERSION}/python", exist_ok=True)
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
                    archive.extractall(path=f"dist/{NAME}{VERSION}")
                # shutil.copytree(python_loc, f"dist/{NAME}{VERSION}/python", dirs_exist_ok=True)
                
                print('Copied python folder...')
                os.chdir(f'dist/{NAME}{VERSION}')


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
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import server

server.main()
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
    # Delete all files and folders except install.sh
    echo "Deleting old files and folders (except install.sh)..."
    find . -type f ! -name "install.sh" -exec rm -f {} +
    find . -type d ! -name "." -exec rm -rf {} +
    echo "Old files and folders deleted."

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
    PKG_DIR="python/'''+python_folder+r'''"
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
python3.12 run.py &
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
</dict>
</plist>
EOF
    python3.12 run.py &
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
    DESKTOP_FILE="$HOME/Desktop/'''+NAME+r'''.desktop"
    echo "Creating Linux desktop shortcut at $DESKTOP_FILE"
    cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name='''+NAME+r'''
Comment=Run '''+NAME+r'''
Exec=$CURRENT_DIR/python/linux/bin/python3.12 $CURRENT_DIR/run.py
Icon=$CURRENT_DIR/'''+png+r'''
Terminal=true
Type=Application
Categories=Utility;
EOF
    chmod +x "$DESKTOP_FILE"
    echo "Launching run.py..."
    python/linux/bin/python3.12 run.py &
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

echo Shortcuts created successfully!
pause'''

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
DefaultDirName={userdocs}\..\..\Downloads\{#AppName}_v{#Version}
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
    ; IconFilename: "{app}\static\{#Icon}"; IconIndex: 0

; Shortcut in the application folder
; Name: "{app}\{#AppName}.lnk"; \
    ; Filename: "{app}\python\windows\python.exe"; \
    ; Parameters: """{app}\run.py"""; \
    ; WorkingDir: "{app}"; \
    ; IconFilename: "{app}\static\{#Icon}"; IconIndex: 0

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
                ico_files = glob.glob(os.path.join('static', '*.ico'))
                ico = ico_files[0]

                # create install.bat/sh for compiling run.go
                NAME = NAME.replace('dist_', '')
                if folder == 'linux':
                    install_script_content = r'''
#!/bin/bash

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
ICON_PATH="$PWD/static/'''+ ico +r'''"
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
echo dirShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
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

        except Exception as e:
            print('Error: '+str(e))
            return


