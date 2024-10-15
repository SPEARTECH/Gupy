from logging import exception
import click
import sys
import os
from target_platforms import *
import platform
import chardet
import subprocess
import shutil
import glob

NAME=''
TARGETS=[]
LANG=''

@click.group()
def cli():
    ##Running checks on python version
    version = '.'.join(sys.version.split(' ')[0].split('.')[:2])
    if float(version) < 3.0:
        raise Exception('Please use Python3+. Make sure you have created a virtual environment.')
    
@click.command()
@click.option(
    '--name',
    '-n',
    required=True,
    help='Name of project'
    )
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'pwa', 'website', 'cli', 'api', 'mobile'], 
        case_sensitive=False
        ),
    multiple=True, 
    default=['desktop'], 
    help="Use this command for each platform you intend to target (ie. -t desktop -t website)"
    )
@click.option(
    '--language',
    '-l',
    type=click.Choice(
        ['py', 'go'], 
        case_sensitive=False
        ),
    multiple=False, 
    # default=['py'], 
    # required=True,
    help="Select the base language for the app ('py' or 'go')"
    )
def create(name,target_platform, language):
    NAME=name #Assigning project name
    LANG=language.lower()
    if '-' in NAME:
        print('Error: Invalid character of "-" in app name. Rename your app to '+ NAME.replace('-','_') +'.')
        return
    elif '.' in NAME:
        print('Error: Invalid character of "." in app name. Rename your app to '+ NAME.replace('.','_') +'.')
        return
    if not LANG and 'pwa' not in target_platform and 'website' not in target_platform:
        print("Error: Option '-l/--language' is required for ['desktop', 'cli', 'api'] targets.")
        return
    elif LANG and LANG != 'py' and LANG != 'go':
        print(f'Incorrect option for --lang/-l\n Indicate "py" or "go" (Python/Golang)')
        return
    elif not LANG and target_platform == ('pwa',):
        LANG = 'js'
    elif not LANG and target_platform == ('website',):
        LANG = 'py'

    dir_list = os.getcwd().split('\\')
    if NAME in dir_list or NAME in os.listdir('.'):
        print('Error: App named '+NAME+' already exists in this location')


    for target in target_platform: #Assigning target platforms
        TARGETS.append(target)
 
    confirmation = click.confirm(f'''
Creating project with the following settings:
Project Name =\t{NAME}
     Targets =\t{TARGETS}
    Language =\t{LANG}

Confirm?  
''', default=True, show_default=True
) #Confirm user's settings

    if confirmation == False: #Exit if settings are incorrect
        click.echo('Exiting...')
        return

    obj = base.Base(NAME)
    obj.create_project_folder() #Create Project folder and ensure correct directory

    if 'desktop' in TARGETS: #create files/folder structure for desktop app if applicable
        desktop.Desktop(NAME,LANG).create()

    if 'pwa' in TARGETS: #create files/folder structure for pwa app if applicable
        pwa.Pwa(NAME).create()

    if 'website' in TARGETS: #create files/folder for django project if applicable
        website.Website(NAME).create()

    if 'cli' in TARGETS: #create files/folder structure for cli app if applicable
        cmdline.CLI(NAME,LANG).create()

    if 'api' in TARGETS:
        print('The API feature is not yet available...')
        return

    if 'mobile' in TARGETS:
        print('The Mobile feature is not yet available...')
        return

@click.command()
# @click.option(
#     '--target-platform',
#     '-t',
#     type=click.Choice(
#         ['desktop', 'pwa', 'website', 'cli', 'api', 'mobile'], 
#         case_sensitive=False
#         ),
#     required=True,
#     multiple=False, 
#     default=['desktop'], 
#     help="Select the app platform you intend to run (ie. -t desktop)"
#     )
def run():
    try:
        # check if target-platform folder exists in path
        print(os.getcwd())
        dir_list = os.getcwd().split('\\')
        def change_dir(dir_list,target):
            if target in dir_list: 
                index = dir_list.index(target)
                chdir_num = len(dir_list) - (index +1)
                if not chdir_num == 0:
                    os.chdir('../'*chdir_num)
        # TARGET=target_platform
        if 'desktop' in dir_list:
            TARGET='desktop'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
            app_obj = desktop.Desktop(NAME)
            app_obj.run()
        elif 'pwa' in dir_list:
            TARGET='pwa'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
            app_obj = pwa.Pwa(NAME)
            app_obj.run()
        elif 'website' in dir_list:
            TARGET='website'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
            app_obj = website.Website(NAME)
            app_obj.run()
        elif 'cli' in dir_list:
            TARGET='cli'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
            app_obj = cmdline.CLI(NAME)
            app_obj.run()

        else:
            print(f'Error: No target platform folder found. Change directory to your app folder and use the create command (ex. cd <path to app>).')
            return
    except Exception as e:
        print('Error: '+str(e))
        print('*NOTE: Be sure to change directory to the desired platform to run (ex. cd <path to target app platform>)*')

@click.command()
@click.option(
    '--file',
    '-f',
    required=True,
    help='File name to compile to binary (required).'
    )
def compile(file):
    try:
        if os.path.exists(file):
            if file.split('.')[-1] == 'py':
                os.system(f'nuitka --standalone --onefile --disable-console {file}')
            elif file.split('.')[-1] == 'go':
                # os.system(f'go mod tidy')
                os.system(f'go build')
    except Exception as e:
        print(e)

@click.command()
@click.option(
    '--file',
    '-f',
    required=True,
    multiple=True, 
    default=[], 
    help="Select a single file to cythonize or select multiple (ie. -f script1.py -f script2.py)."
    )
def cythonize(file):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if '-' in os.getcwd().split('\\')[-1]:
        print('Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split('\\')[-1].replace('-','_') +'.')
        return
    elif '.' in os.getcwd().split('\\')[-1]:
        print('Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split('\\')[-1].replace('.','_') +'.')
        return

    for item in file:
        print(f'Building {item} file...')
        os.system(f'cythonize -i {os.path.splitext(item)[0]}.py')

@click.command()
@click.option(
    '--file',
    '-f',
    required=True,
    multiple=True, 
    default=[], 
    help='Select a single file to gopherize or select multiple (ie. -f module1.go -f module2.go).'
    )
def gopherize(file):
    if '-' in os.getcwd().split('\\')[-1]:
        print('Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split('\\')[-1].replace('-','_') +'.')
        return
    elif '.' in os.getcwd().split('\\')[-1]:
        print('Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split('\\')[-1].replace('.','_') +'.')
        return

    for item in file:
        print(f'Building {item} file...')
        os.system(f'go build -o {os.path.splitext(item)[0]}.so -buildmode=c-shared {item} ')

@click.command()
def assemble():
    dir_list = os.getcwd().split('\\')
    def change_dir(dir_list,target):
        if target in dir_list: 
            index = dir_list.index(target)
            chdir_num = len(dir_list) - (index)
            if not chdir_num == 0:
                os.chdir('../'*chdir_num)
    # detect the platform in the current directory or parent directories and then change directory to its root for operation
    if 'desktop' in dir_list:
        TARGET='desktop'
        change_dir(dir_list,TARGET)
        NAME=os.path.basename(os.getcwd())
    elif 'pwa' in dir_list:
        TARGET='pwa'
        change_dir(dir_list,TARGET)
        NAME=os.path.basename(os.getcwd())
    elif 'website' in dir_list:
        TARGET='website'
        change_dir(dir_list,TARGET)
        NAME=os.path.basename(os.getcwd())
    elif 'cli' in dir_list or 'api' in dir_list or 'mobile' in dir_list:
        print('Error: --assemble is only available for desktop, pwa, and website projects.')
        return
    else:
        print(f'Error: No target platform folder found. Change directory to your app and try again (ex. cd <path to app>).')
        return

    if TARGET == 'desktop':
        app_obj = desktop.Desktop(NAME)
        app_obj.assemble()
    elif TARGET == 'website':
        app_obj = website.Website(NAME)
        app_obj.assemble()
    elif TARGET == 'pwa':
        app_obj = pwa.Pwa(NAME)
        app_obj.assemble()
    else:
        print('Platform not enabled for assembly. Change directory to your app root folder with desktop, pwa, or website platforms (ex. cd <path to app>/<platform>).')

@click.command()
def package():
    try:
        dir_list = os.getcwd().split('\\')
        def change_dir(dir_list,target):
            index = dir_list.index(target)
            chdir_num = len(dir_list) - (index +1)
            if not chdir_num == 0:
                os.chdir('../'*chdir_num)
        # detect the platform in the current directory or parent directories and then change directory to its root for operation
        if 'desktop' in dir_list:
            TARGET='desktop'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
        elif 'cli' in dir_list:
            TARGET='cli'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
        elif 'pwa' in dir_list or 'website' in dir_list:
            print('Error: --package is only available for desktop, and cli projects.')
            return
        else:
            print(f'Error: No target platform folder found. Change directory to your app folder and use the create command (ex. cd <path to app>).')
            return

        NAME = 'pkg_'+NAME
        # creating project folder if doesnt already exist
        os.makedirs(NAME, exist_ok=True)

        # copying all files into project folder for packaging
        files = os.listdir(os.cwd())
        folders = []
        for file_name in files:
            full_file_name = os.path.join(os.getcwd(), file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, NAME)
            elif os.path.isdir(full_file_name) and file_name != NAME:
                shutil.copytree(full_file_name, NAME)
        # prompt user to modify files and toml and run package again

        # checking for requirements.txt to add to pyproject.toml
        file_path = 'requirements.txt'

        if 'requirements.txt' in os.listdir('.'):
            # Detect the encoding of the file
            def detect_file_encoding(file_path):
                with open(file_path, 'rb') as f:
                    raw_data = f.read(10000)  # Read a portion of the file to detect encoding
                    result = chardet.detect(raw_data)
                    return result['encoding']
            encoding = detect_file_encoding(file_path)

            with open('requirements.txt', 'r', encoding=encoding) as f:
                # Strip newline characters and empty spaces from each requirement
                requirements = [line.strip() for line in f.readlines()]
        else:
            requirements = []

        # Join requirements into a multiline string for the TOML file
        requirements_string = ',\n'.join(f'"{req}"' for req in requirements)


        # # Join requirements into a multiline string for the TOML file
        # requirements_string = ',\n'.join(f'"{req}"' for req in requirements)

        toml_content = f'''
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "'''+NAME+'''"
version = "0.0.1"
authors = [
{ name="Example Author", email="author@example.com" },
]
description = "A small example package"
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
"Programming Language :: Python :: 3",
"License :: OSI Approved :: MIT License",
"Operating System :: OS Independent",
]

# Add your dependencies here
dependencies = [
'''+ str(requirements_string) +f'''
]

[project.urls]
Homepage = "https://github.com/pypa/sampleproject"
Issues = "https://github.com/pypa/sampleproject/issues"


# Specify the directory where your Python package code is located
[tool.hatch.build.targets.sdist]
include = ["*"]

[tool.hatch.build.targets.wheel]
include = ["*"]

# Define entry points for CLI
[project.scripts]
'''+f'''{NAME} = "{NAME}.__main__:main"'''

        readme_content = f'''
# {NAME} Project
'''
        license_content = '''
MIT License

Copyright (c) 2022 SPEARTECH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
        # add check here for platform type and language 
        system = platform.system()

        if system == 'Darwin':
            cmd = 'python3'
        elif system == 'Linux':
            cmd = 'python'
        else:
            cmd = 'python'
        # os.chdir('../')
        print('checking for README.md...')
        if 'README.md' not in os.listdir('.'):
            f = open('README.md', 'x')
            f.write(readme_content)
            print(f'created "README.md" file.')
            f.close()
        print('checking for LICENSE...')
        if 'LICENSE' not in os.listdir('.'):
            f = open('LICENSE', 'x')
            f.write(license_content)
            print(f'created "LICENSE" file.')
            f.close()
        print('checking for pyproject.toml...')
        if 'pyproject.toml' not in os.listdir('.'):
            f = open('pyproject.toml', 'x')
            f.write(toml_content)
            print(f'created "pyproject.toml" file.')
            f.close()
            print('pyproject.toml created with default values. Modify it to your liking and rerun the package command.')
            if requirements_string == '':
                print('*Note: No requirements.txt was found. Create this file and delete the pyproject.toml to populate the dependencies for the whl package (ex. python -m pip freeze > requirements.txt)*')
            return
        os.system(f'{cmd} -m build')
    except Exception as e:
        print('Error: '+str(e))
        print('*NOTE: Be sure to change directory to the desired platform to package (ex. cd <path to target app platform>)*')

@click.command()
@click.option(
    '--version',
    '-v',
    required=True,
    help='Desired version for distribution (ie. -v 1.0.0).'
    )
def distribute(version):
    VERSION = version.replace('.','_')
    try:
        dir_list = os.getcwd().split('\\')
        def change_dir(dir_list,target):
            index = dir_list.index(target)
            chdir_num = len(dir_list) - (index +1)
            if not chdir_num == 0:
                os.chdir('../'*chdir_num)
        # detect the platform in the current directory or parent directories and then change directory to its root for operation
        if 'desktop' in dir_list:
            TARGET='desktop'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
        # perhaps run logic for .pyd/.so files, moving all that are to be deployed...? mobile to apk?
        elif 'pwa' in dir_list or 'website' in dir_list or 'api' in dir_list or 'mobile' in dir_list or 'cli' in dir_list:
            print('Error: --distribute is only available for desktop projects.')
            return
        else:
            print(f'Error: No target platform folder found. Change directory to your app folder and use the create command (ex. cd <path to app>).')
            return

        # creating project folder if doesnt already exist
        NAME = 'dist_'+NAME
        os.makedirs(NAME, exist_ok=True)
        os.chdir(NAME)

        # creating version folder is doesnt already exist
        os.makedirs(VERSION, exist_ok=True)
        shutil.rmtree(VERSION)
        os.makedirs(VERSION, exist_ok=True)
        os.chdir(VERSION)

        # detect os and make folder
        system = platform.system()

        if system == 'Darwin':
            system = 'darwin'
            folder = 'mac'
        elif system == 'Linux':
            system = 'linux'
            folder = 'linux'
        else:
            system = 'win'
            folder = 'windows'

        os.makedirs(folder, exist_ok=True)
        shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
        os.chdir('../../')

        # move files+folders into project folder if just created
        if folder == 'linux' or folder == 'mac':
            comp_file_ext = 'so'
        elif folder == 'windows':
            comp_file_ext = 'pyd'

        # get python location
        python_loc = os.path.dirname(sys.executable)
        python_executable = sys.executable.split('\\')[-1]
        python_version = "".join(sys.version.split(' ')[0].split('.')[0:2]) 
        # print(os.getcwd())
        # moves files and folders - only checks the cythonized files in root directory.
        files = os.listdir(os.getcwd())
        folders = []
        for file_name in files:
            full_file_name = os.path.join(os.getcwd(), file_name)
            if os.path.isfile(full_file_name):
                if comp_file_ext in file_name.split('.')[-1] and system in file_name:
                    shutil.copy(full_file_name, f"{NAME}/{VERSION}/{folder}")
                elif comp_file_ext in file_name.split('.')[-1] and system in file_name:
                    shutil.copy(full_file_name, f"{NAME}/{VERSION}/{folder}")
                elif file_name.split('.')[-1] != 'pyd' and file_name.split('.')[-1] != 'so':
                    shutil.copy(full_file_name, f"{NAME}/{VERSION}/{folder}")
            elif os.path.isdir(full_file_name) and file_name != NAME:
                shutil.copytree(full_file_name, f"{NAME}/{VERSION}/{folder}/{file_name}", dirs_exist_ok=True)
            print('Copied '+file_name+' to '+f"{NAME}/{VERSION}/{folder}/{file_name}"+'...')
        # package latest python if not selected - make python folder with windows/mac/linux
        os.makedirs(f"{NAME}/{VERSION}/{folder}/python", exist_ok=True)
        print('Copied python folder...')
        shutil.copytree(python_loc, f"{NAME}/{VERSION}/{folder}/python", dirs_exist_ok=True)
        # install requirements with new python location if it exists
        if os.path.exists('requirements.txt'):
            if folder == 'windows':
                command = f".\\{NAME}\\{VERSION}\\{folder}\\python\\{python_executable} -m pip install -r requirements.txt"
            else:
                command = f".\\{NAME}\\{VERSION}\\{folder}\\python\\lib\\{python_executable} -m pip install -r requirements.txt"
            # Run the command
            result = subprocess.run(command, shell=True, check=True)
            # Check if the command was successful
            if result.returncode == 0:
                print("Requirements installed successfully.")
            else:
                print("Failed to install requirements.txt - ensure it exists.")

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
        subprocess.run(f'.\\go\\bin\\go.exe mod init example.com/{NAME}', shell=True, check=True)
        # subprocess.run(f'.\\go\\bin\\go.exe mod tidy', shell=True, check=True)
        # Use glob to find all .ico files in the folder
        ico_files = glob.glob(os.path.join('static', '*.ico'))
        ico = ico_files[0]

        # create install.bat/sh for compiling run.go
        if folder == 'mac' or folder == 'linux':
            run_go_content = r'''
package main

import (
    "fmt"
    "os"
    "path/filepath"
	"os/exec"
)

func main() {

    // Run the Python script
    runPythonScript()
}

// Runs the Python script 'gui.py'
func runPythonScript() {
    currentDir, err := filepath.Abs(filepath.Dir(os.Args[0]))
    if err != nil {
        fmt.Println("Error getting current directory:", err)
        return
    }

    pythonExe := filepath.Join(currentDir, "python", "lib", "'''+ python_executable +r'''") 
    scriptPath := filepath.Join(currentDir, "__main__.py")

    fmt.Printf("Current directory is: %s\n", currentDir)
    fmt.Printf("Running Python script %s...\n", scriptPath)

    cmd := exec.Command(pythonExe, scriptPath)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr

    err = cmd.Run()
    if err != nil {
        fmt.Println("Error running Python script:", err)
    }
}'''        
            install_script_content = r'''
#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"
sudo chmod 755 python/lib/'''+ python_executable +r'''

echo "Compiling run.go..."
go/bin/go build run.go

if [ $? -ne 0 ]; then
    echo "Go build failed. Exiting..."
    exit 1
fi

# Define paths for the icon and the target executable
ICON_PATH="$PWD/static/'''+ ico +r'''"
TARGET_PATH="$PWD/run"

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
            with open('run.go', 'w') as f:
                f.write(run_go_content)
        else:
            run_go_content = r'''
package main

import (
    "fmt"
    "os"
    "path/filepath"
	"os/exec"
)

func main() {

    // Run the Python script
    runPythonScript()
}

// Runs the Python script 'gui.py'
func runPythonScript() {
    currentDir, err := filepath.Abs(filepath.Dir(os.Args[0]))
    if err != nil {
        fmt.Println("Error getting current directory:", err)
        return
    }

    pythonExe := filepath.Join(currentDir, "python", "'''+ python_executable +r'''") 
    scriptPath := filepath.Join(currentDir, "__main__.py")

    fmt.Printf("Current directory is: %s\n", currentDir)
    fmt.Printf("Running Python script %s...\n", scriptPath)

    cmd := exec.Command(pythonExe, scriptPath)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr

    err = cmd.Run()
    if err != nil {
        fmt.Println("Error running Python script:", err)
    }
}'''        
            install_script_content = r'''
@echo off
cd /d "%~dp0"

%~dp0go/bin/go.exe build run.go

if %errorlevel% neq 0 (
    echo Go build failed. Exiting...
    exit /b 1
)

REM Create a VBScript to make a desktop shortcut with an icon
echo Set objShell = CreateObject("WScript.Shell") > CreateShortcut.vbs
echo Set desktopShortcut = objShell.CreateShortcut(objShell.SpecialFolders("Desktop") ^& "\\'''+NAME+r'''.lnk") >> CreateShortcut.vbs
echo desktopShortcut.TargetPath = "%cd%\run.exe" >> CreateShortcut.vbs
echo desktopShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo desktopShortcut.Save >> CreateShortcut.vbs

REM Create a shortcut in the same directory as run.exe
echo Set dirShortcut = objShell.CreateShortcut("%cd%\\'''+NAME+r'''.lnk") >> CreateShortcut.vbs
echo dirShortcut.TargetPath = "%cd%\run.exe" >> CreateShortcut.vbs
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
            with open('run.go', 'w') as f:
                f.write(run_go_content)

    except Exception as e:
        print('Error: '+str(e))
        return

# @click.command()
# @click.option(
#     '--file',
#     '-f',
#     required=True,
#     multiple=True, 
#     default=[], 
#     help='Select a single javascript file to obfuscate or select multiple (ie. -f view1.html -f view2.html).'
#     )
# def obfuscate():
#     try:
#         # for each file, obfuscate javascript (test with html file + vue options api - select lib to do this)
#         pass
#     except Exception as e:
#         print('Error: '+str(e))
#         return


def main():
    cli.add_command(create) #Add command for cli
    cli.add_command(run) #Add command for cli
    cli.add_command(compile)
    cli.add_command(cythonize)
    cli.add_command(gopherize)
    cli.add_command(assemble)
    cli.add_command(package)
    cli.add_command(distribute)
    # cli.add_command(obfuscate)

    cli() #Run cli

if __name__ == '__main__':
    main()