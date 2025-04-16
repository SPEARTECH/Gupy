from logging import exception
import click
from target_platforms import *
import platform
import sys
import os
import chardet
import subprocess
import shutil
import glob
from colorama import Fore, Style
import py7zr

NAME=''
TARGETS=[]
LANG=''


@click.group()
def cli():
    """
.........................-=+##+*@**#=............................
........................##==*%+=*#++%+-==+++==-:.................
......................-*@%+==*###%%%#**+====++*###*=:............
.....................+%=-=***#%%*=-    :.........:=*##+:.........
....................:%%*++*#%*-  -===------        ..-*#*-.......
...................+%+-=*%%+  -=+++=+*######*=        :+@@*=:....
...................#%**#%+:-=+++++#%#=-    -++        -+--=*%*:..
.......-++++=:......-#@*--==++++*%#-      :         :       *@=.
......-@#=-=*%*:....*%=-++++++++%#    +%@@#*+         =%@%*+:.*@-
:=****#@+=-:.:*%-.-%#=+****#**+#@-   #@%+*=.*%       +@#++:+%.:@*
@#+=-=#@*=====:*%+%#+*#%####%%#%@:  -@@#:=%%%@-      #@=:#%%@-.%#
@#====+*###*+++=%@#+#%#-  :--+*%@=   #@@@@@@@#       =%@@@%%#.:@+
=@#+++===+*####%%*+*#%#++++****#@+.  :=**#%#+         =*%%#+..#%:
.-#%#########%@%*****#@%####*+*%*.  :     -     ==-------    :#%:
.:#%*======+*#%%%#**#%%=----=*%%=.              +@%%%%%#-    :+@-
=@*:.:-=++**+*%@@#*###%%%##%%%##+.              -#*+*%%=      #%.
@*.-=+#@#=--+##%%%%%%%%##########-              :-***+-      *@=.
%%*++*@#==+##*#+%%@%%%%%##########=---            :--      -#@=..
:*%%*#@******#=+@-*@@%%%%%######%%%#+==----          :---=+%%-...
..:=*#%###%#+-+%=..:*@@%%%%%%%%%%%%%%##*++=====---======+#%+.....
.......:--##*#*:.....:=*%@%%%%######%%%%%*============*%%*:......
...........--...........:+#@@%%####%%##*+=========++#%#+:........
...........................-+*#%%%%#*+=======++*##%#+-...........
...............................:=+*###%%#######*+-:..............
.................................................................
................ ▄▄▄▄▄▄▄ ▄▄   ▄▄ ▄▄▄▄▄▄▄ ▄▄   ▄▄ ▄▄ .............
................█       █  █ █  █       █  █ █  █  █.............
................█   ▄▄▄▄█  █ █  █    ▄  █  █▄█  █  █.............
................█  █  ▄▄█  █▄█  █   █▄█ █       █  █.............
................█  █ █  █       █    ▄▄▄█▄     ▄█▄▄█.............
................█  █▄▄█ █       █   █     █   █  ▄▄ .............
................█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄█     █▄▄▄█ █▄▄█.............
.................................................................
............ Simplifying Cross-Platform development with ........
....................... Go, Vue, and Python .....................
"""

    ##Running checks on python version
    version = '.'.join(sys.version.split(' ')[0].split('.')[:2])
    if float(version) < 3.0:
        raise Exception('Please use Python3+. Make sure you have created a virtual environment.')
    click.echo("Gupy! v0.3.9")
    go,gcc,cgo = check_status()
    if go == 'True':
        click.echo(f'Go\t{Fore.GREEN}{go}{Style.RESET_ALL}')
    else:
        click.echo(f'Go\t{Fore.RED}{go}{Style.RESET_ALL}')    
    if gcc == 'True':
        click.echo(f'Gcc\t{Fore.GREEN}{gcc}{Style.RESET_ALL}')
    else:
        click.echo(f'Gcc\t{Fore.RED}{gcc}{Style.RESET_ALL}')
    if cgo == 'True':
        click.echo(f'Cgo\t{Fore.GREEN}{cgo}{Style.RESET_ALL}')
    else:
        click.echo(f'Cgo\t{Fore.RED}{cgo}{Style.RESET_ALL}')

    
@click.command(help='Creates an app template for desired target platforms')
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
        ['desktop', 'pwa', 'website', 'cli', 'api', 'mobile', 'script'], 
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
    # detect os and make folder
    system = platform.system()

    if system == 'Darwin' or system == 'Linux':
        delim = '/'
    else:
        delim = '\\'

    dir_list = os.getcwd().split(delim)    
    NAME=name.replace(' ','_').replace('.','_').replace('-','_') #Assigning project name
    if language:
        LANG=language.lower()
    else:
        LANG = ''
    if '-' in NAME:
        click.echo(f'{Fore.RED}Error: Invalid character of "-" in app name. Rename your app to '+ NAME.replace('-','_') +f'.{Style.RESET_ALL}')
        return
    elif '.' in NAME:
        click.echo(f'{Fore.RED}Error: Invalid character of "." in app name. Rename your app to '+ NAME.replace('.','_') +f'.{Style.RESET_ALL}')
        return
    if not LANG and 'pwa' not in target_platform and 'mobile' not in target_platform:
        click.echo(f"{Fore.RED}Error: Option '-l/--language' is required for ['desktop', 'website', 'cli', 'api', 'script'] targets.{Style.RESET_ALL}")
        return
    elif LANG and LANG != 'py' and LANG != 'go':
        click.echo(f'{Fore.RED}Incorrect option for --lang/-l\n Indicate "py" or "go" (Python/Golang){Style.RESET_ALL}')
        return
    elif not LANG and (target_platform == ('pwa',) or target_platform == ('mobile',) or target_platform == ('pwa','mobile',)):
        LANG = 'js'

    dir_list = os.getcwd().split(delim)
    if NAME in dir_list or NAME in os.listdir('.'):
        click.echo(f'{Fore.YELLOW}App named '+NAME+f' already exists in this location{Style.RESET_ALL}')


    for target in target_platform: #Assigning target platforms
        TARGETS.append(target)
 
    confirmation = click.confirm(f'''
Creating project with the following settings:
Project Name =\t{NAME}
     Targets =\t{TARGETS}
    Language =\t{Fore.BLUE if LANG == 'go' else Fore.YELLOW if LANG == 'py' else Fore.CYAN}{LANG}{Style.RESET_ALL}

Confirm?  
''', default=True, show_default=True
) #Confirm user's settings

    if confirmation == False: #Exit if settings are incorrect
        click.echo(f'{Fore.GREEN}Exiting...{Style.RESET_ALL}')
        return

    obj = base.Base(NAME)
    obj.create_project_folder() #Create Project folder and ensure correct directory

    if 'desktop' in TARGETS: #create files/folder structure for desktop app if applicable
        desktop.Desktop(NAME,LANG).create()

    if 'pwa' in TARGETS: #create files/folder structure for pwa app if applicable
        pwa.Pwa(NAME).create()

    if 'website' in TARGETS: #create files/folder for django project if applicable
        # if LANG == 'go':
        #     click.echo(f'{Fore.RED}Go Website feature is not yet available...{Style.RESET_ALL}')
        #     return
        website.Website(NAME,LANG).create()

    if 'cli' in TARGETS: #create files/folder structure for cli app if applicable
        # if LANG == 'go':
        #     click.echo(f'{Fore.RED}Go CLI feature is not yet available...{Style.RESET_ALL}')
        #     return
        cmdline.CLI(NAME,LANG).create()

    if 'script' in TARGETS: #create files/folder structure for script app if applicable
        script.Script(NAME,LANG).create()

    if 'api' in TARGETS:
        # click.echo(f'{Fore.RED}The API feature is not yet available...{Style.RESET_ALL}')
        # return
        api.Api(NAME,LANG).create()

    if 'mobile' in TARGETS:
        # click.echo(f'{Fore.RED}The Mobile feature is not yet available...{Style.RESET_ALL}')
        # return
        mobile.Mobile(NAME).create()

@click.command(help='Runs the app in current platform directory\n\nSupported target platforms:\n\n.... Desktop\n\n.... PWA\n\n.... Website\n\n.... API\n\n.... CLI\n\n.... ETL Pipeline')
def run():
    # detect os and make folder
    system = platform.system()

    if system == 'Darwin' or system == 'Linux':
        delim = '/'
    else:
        delim = '\\'
    try:
        # check if target-platform folder exists in path
        print(os.getcwd())
        dir_list = os.getcwd().split(delim)
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
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = desktop.Desktop(NAME)
            app_obj.run()
        elif 'pwa' in dir_list:
            TARGET='pwa'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = pwa.Pwa(NAME)
            app_obj.run()
        elif 'website' in dir_list:
            TARGET='website'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = website.Website(NAME,LANG)
            app_obj.run()
        elif 'cli' in dir_list:
            TARGET='cli'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = cmdline.CLI(NAME)
            app_obj.run()
        elif 'script' in dir_list:
            TARGET='script'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = script.Script(NAME)
            app_obj.run()
        elif 'api' in dir_list:
            TARGET='api'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = api.Api(NAME)
            app_obj.run()
        elif 'mobile' in dir_list:
            TARGET='mobile'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = mobile.Mobile(NAME)
            app_obj.run()
        elif 'etl' in dir_list:
            TARGET='etl'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1]
            app_obj = etl.Etl(NAME)
            app_obj.run()
        else:
            click.echo(f'{Fore.RED}Error: No target platform folder found. Change directory to your app folder and use the create command (ex. cd <path to app>).{Style.RESET_ALL}')
            return
    except Exception as e:
        print('Error: '+str(e))
        print('*NOTE: Be sure to change directory to the desired platform to run (ex. cd <path to target app platform>)*')

@click.command(help='Compiles py and go files into exe binaries')
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
                os.system(f'nuitka {file}')
            elif file.split('.')[-1] == 'go':
                # os.system(f'go mod tidy')
                os.system(f'go build {file}')
    except Exception as e:
        print(e)

@click.command(help='Compiles py files into c-shared modules')
@click.option(
    '--file',
    '-f',
    required=True,
    multiple=True, 
    default=[], 
    help="Select a single file to cythonize or select multiple (ie. -f script1.py -f script2.py)."
    )
def cythonize(file):
    # detect os and make folder
    system = platform.system()

    if system == 'Darwin' or system == 'Linux':
        delim = '/'
    else:
        delim = '\\'
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if '-' in os.getcwd().split(delim)[-1]:
        click.echo(f'{Fore.RED}Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split(delim)[-1].replace('-','_') +f'.{Style.RESET_ALL}')
        return
    elif '.' in os.getcwd().split(delim)[-1]:
        click.echo(f'{Fore.RED}Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split(delim)[-1].replace('.','_') +f'.{Style.RESET_ALL}')
        return

    for item in file:
        print(f'Building {item} file...')
        os.system(f'cythonize -i {os.path.splitext(item)[0]}.py')

@click.command(help='Compiles go files into c-shared modules')
@click.option(
    '--file',
    '-f',
    required=True,
    multiple=True, 
    default=[], 
    help='Select a single file to gopherize or select multiple (ie. -f module1.go -f module2.go).'
    )
def gopherize(file):
    # detect os and make folder
    system = platform.system()

    if system == 'Darwin' or system == 'Linux':
        delim = '/'
    else:
        delim = '\\'
    if '-' in os.getcwd().split(delim)[-1]:
        click.echo(f'{Fore.RED}Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split(delim)[-1].replace('-','_') +f'.{Style.RESET_ALL}')
        return
    elif '.' in os.getcwd().split(delim)[-1]:
        click.echo(f'{Fore.RED}Error: Invalid character of "-" in current folder name. Rename this folder to '+ os.getcwd().split(delim)[-1].replace('.','_') +f'.{Style.RESET_ALL}')
        return

    for item in file:
        print(f'Building {item} file...')
        os.system(f'go build -o {os.path.splitext(item)[0]}.so -buildmode=c-shared {item} ')

def check_status():
    # Check gupy dependancies when ran
    def is_go_in_path():
        return shutil.which("go") is not None
    
    # If go is not found, prompt user
    if not is_go_in_path():
        click.echo(f"{Fore.RED}go not found in PATH. Download Go at https://go.dev/doc/install or add the go/bin folder to PATH.{Style.RESET_ALL}")
        return 'False','False','False'

    #checking if gcc.exe is in path for windows users for gopherize command
    def is_gcc_in_path():
        return shutil.which("gcc") is not None

    def is_cc_in_path():
        return shutil.which("cc") is not None


    system = platform.system()

    if system == 'Darwin' or system == 'Linux':
        pass
    else:
        result = subprocess.run(["go", "env", "GOPATH"], capture_output=True, text=True, check=True)
        goroot = result.stdout.strip()

        # # Function to copy contents from source to destination (merging files)
        # def copy_folder_contents(src, dest):
        #     if not os.path.exists(src):  # Skip if source folder doesn't exist
        #         return

        #     os.makedirs(dest, exist_ok=True)  # Ensure destination exists

        #     for item in os.listdir(src):
        #         src_path = os.path.join(src, item)
        #         dest_path = os.path.join(dest, item)

        #         if os.path.isdir(src_path):
        #             copy_folder_contents(src_path, dest_path)  # Recursively copy subfolders
        #         else:
        #             shutil.copy2(src_path, dest_path)  # Copy file, overwriting if necessary

        # Check if gcc or cc is in PATH
        if not is_gcc_in_path() or not is_cc_in_path():
            # try:
            #     # Define the source and destination directories
            #     src_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mingw64")
            #     dest_root = goroot

            #     # List of directories to copy
            #     folders = ["bin", "etc", "include", "lib", "share"]

            #     for folder in folders:
            #         source = os.path.join(src_root, folder)
            #         destination = os.path.join(dest_root, folder)

            #         print(f"Merging {folder}...")

            #         copy_folder_contents(source, destination)

            #     print(f"Merged mingw64 files into {goroot}. Try running `gupy check` again.")

            # except Exception as e:
            #     print(e)
            #     return 'True', 'False', 'False'
            click.echo(f'{Fore.RED}gcc and/or cc is not a valid command; Add their bin folder to PATH and/or follow the instructions at https://www.msys2.org/ and restart the terminal session.{Style.RESET_ALL}')
            return 'True', 'False', 'False'
    try:
        subprocess.run(["go", "env", "-w", "CGO_ENABLED=1{Style.RESET_ALL}"], check=True)
        # print("Successfully set CGO_ENABLED=1")
        return 'True','True','True'
    except subprocess.CalledProcessError as e:
        click.echo(f"{Fore.RED}Error setting CGO_ENABLED:{Style.RESET_ALL} {e}")
        return 'True','True','False'
    except FileNotFoundError:
        click.echo(f"{Fore.RED}Go is not installed or not in PATH.{Style.RESET_ALL}")
        return 'True','True','False'
        
@click.command(help='''Checks dependency commands in PATH\n\n.... Go\t\tRuns go commands\n\n.... Gcc\tCompiles py files to cython binaries\n\n.... Cgo\tCompiles go files to so binaries''')
def check():
    # go,gcc,cgo = check_status()
    # if go == 'True':
    #     print(f'Go\t{Fore.GREEN}{go}{Style.RESET_ALL}')
    # else:
    #     print(f'Go\t{Fore.RED}{go}{Style.RESET_ALL}')    
    # if gcc == 'True':
    #     print(f'Gcc\t{Fore.GREEN}{gcc}{Style.RESET_ALL}')
    # else:
    #     print(f'Gcc\t{Fore.RED}{gcc}{Style.RESET_ALL}')
    # if cgo == 'True':
    #     print(f'Cgo\t{Fore.GREEN}{cgo}{Style.RESET_ALL}')
    # else:
    #     print(f'Cgo\t{Fore.RED}{cgo}{Style.RESET_ALL}')
    return # code check executes with every command given, this just needs to return it

@click.command(help='Re-compiles all webassembly code in your go_wasm folder\n\nSupported target platforms:\n\n.... Desktop\n\n.... PWA\n\n.... Website')
def assemble():
    # detect os and make folder
    system = platform.system()

    if system == 'Darwin' or system == 'Linux':
        delim = '/'
    else:
        delim = '\\'
    dir_list = os.getcwd().split(delim)
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
        NAME=os.path.basename(os.getcwd()).replace(' ','_')
    elif 'pwa' in dir_list:
        TARGET='pwa'
        change_dir(dir_list,TARGET)
        NAME=os.path.basename(os.getcwd()).replace(' ','_')
    elif 'website' in dir_list:
        TARGET='website'
        change_dir(dir_list,TARGET)
        NAME=os.path.basename(os.getcwd()).replace(' ','_')
    elif 'cli' in dir_list or 'api' in dir_list or 'mobile' in dir_list or 'script' in dir_list:
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

@click.command(help='Packages a python app for upload to pypi.org')
def package():
    # detect os and make folder
    system = platform.system()

    if system == 'Darwin' or system == 'Linux':
        delim = '/'
    else:
        delim = '\\'
    try:
        dir_list = os.getcwd().split(delim)
        def change_dir(dir_list,target):
            index = dir_list.index(target)
            chdir_num = len(dir_list) - (index +1)
            if not chdir_num == 0:
                os.chdir('../'*chdir_num)
        # detect the platform in the current directory or parent directories and then change directory to its root for operation
        if 'desktop' in dir_list:
            TARGET='desktop'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1].replace(' ','_')
        elif 'cli' in dir_list:
            TARGET='cli'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1].replace(' ','_')
        elif 'script' in dir_list:
            TARGET='script'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1].replace(' ','_')
        elif 'pwa' in dir_list or 'website' in dir_list or 'mobile' in dir_list or 'etl' in dir_list:
            click.echo(f'{Fore.RED}Error: --package is only available for desktop, cli, and script python projects.{Style.RESET_ALL}')
            return
        else:
            click.echo(f'{Fore.RED}Error: No target platform folder found. Change directory to your app folder and use the create command (ex. cd <path to app>).{Style.RESET_ALL}')
            return

        # creating project folder if doesnt already exist
        os.makedirs(NAME, exist_ok=True)

        # copying all files into project folder for packaging
        files = os.listdir(os.getcwd())
        for file_name in files:
            full_file_name = os.path.join(os.getcwd(), file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, NAME)
            elif os.path.isdir(full_file_name) and file_name != NAME and file_name != 'dist':
                shutil.copytree(full_file_name, f"{NAME}/{file_name}", dirs_exist_ok=True)
        
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
classifiers = ['''+r'''
"Programming Language :: Python :: 3",
"License :: OSI Approved :: MIT License",
"Operating System :: OS Independent",
]
'''+'''
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
'''
        if TARGET != 'script':
                toml_content += f'''
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
        # assign current python executable to use
        cmd = sys.executable.split(delim)[-1]
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
            click.echo(f'{Fore.GREEN}pyproject.toml created with default values. Modify it to your liking and rerun the package command.{Style.RESET_ALL}')
            if requirements_string == '':
                click.echo(f'*{Fore.YELLOW}Note:{Style.RESET_ALL} No requirements.txt was found. Create this file and delete the pyproject.toml to populate the dependencies for the whl package (ex. python -m pip freeze > requirements.txt)*')
            return
        os.system(f'{cmd} -m build')
        print(f'Removing temporary project folder: {NAME}')
        shutil.rmtree(NAME)

    except Exception as e:
        click.echo(f'{Fore.RED}Error: {Style.RESET_ALL}'+str(e))
        click.echo(f'*{Fore.YELLOW}NOTE:{Style.RESET_ALL} Be sure to change directory to the desired platform to package (ex. cd <path to target app platform>)*')

@click.command(help='Packages desktop apps for distribution with install script')
@click.option(
    '--version',
    '-v',
    required=True,
    help='Desired version for distribution (ie. -v 1.0.0).'
    )
def distribute(version):
    VERSION = 'v'+version.replace('.','').replace('-','').replace('_','')
    try:
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin':
            system = 'darwin'
            delim = '/'
        elif system == 'Linux':
            system = 'linux'
            delim = '/'
        else:
            system = 'win'
            folder = 'windows'
            delim = '\\'


        dir_list = os.getcwd().split(delim)
        def change_dir(dir_list,target):
            index = dir_list.index(target)
            chdir_num = len(dir_list) - (index +1)
            if not chdir_num == 0:
                os.chdir('../'*chdir_num)
        # detect the platform in the current directory or parent directories and then change directory to its root for operation
        if 'desktop' in dir_list:
            TARGET='desktop'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split(delim)[-1].replace(' ','_')

        # perhaps run logic for .pyd/.so files, moving all that are to be deployed...? mobile to apk?
        elif 'pwa' in dir_list or 'website' in dir_list or 'api' in dir_list or 'mobile' in dir_list or 'cli' in dir_list or 'script' in dir_list or 'etl' in dir_list:
            print('Error: --distribute is only available for desktop projects.')
            return
        else:
            print(f'Error: No target platform folder found. Change directory to your app folder and use the create command (ex. cd <path to app>).')
            return

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
        
        # get python location and executable
        if system in ['linux', 'darwin']:
            python_loc = gupy_file_path + '/python'
            python_folder = 'unix/bin'
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
        archive_path = python_loc + delim + 'python.7z'
        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            archive.extractall(path=f"dist/{NAME}{VERSION}/python")
        # shutil.copytree(python_loc, f"dist/{NAME}{VERSION}/python", dirs_exist_ok=True)
        
        print('Copied python folder...')
        os.chdir(f'dist/{NAME}{VERSION}')


        command = f".{delim}python{delim}{python_folder}{delim}{python_executable} python{delim}{python_folder}{delim}get-pip.py"
        # Run the command
        result = subprocess.run(command, shell=True, check=True)

        command = f".{delim}python{delim}{python_folder}{delim}{python_executable} -m pip install --upgrade pip"
        # Run the command
        result = subprocess.run(command, shell=True, check=True)

        # install requirements with new python location if it exists
        if os.path.exists('requirements.txt'):
                # Read as binary to detect encoding
            with open('requirements.txt', 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')

            with open('requirements.txt', 'r', encoding=encoding) as f:
                if len(f.readlines()) > 0:
                    command = f".{delim}python{delim}{python_folder}{delim}{python_executable} -m pip install -r requirements.txt"

                    # Run the command
                    result = subprocess.run(command, shell=True, check=True)
                    # Check if the command was successful
                    if result.returncode == 0:
                        print("Requirements installed successfully.")
                    else:
                        print("Failed to install requirements.txt - ensure it exists.")

        # subprocess.run(f'.\\go\\bin\\go.exe mod tidy', shell=True, check=True)
        # Use glob to find all .ico files in the folder
        ico_files = glob.glob(os.path.join('static', '*.ico'))
        ico = ico_files[0]

        png_files = glob.glob(os.path.join('static', '*.png'))
        png = png_files[0]

        print("Please enter Github information for the app where your release package will be uploaded...")
        REPO_OWNER = input(f'Enter the Github repository owner: ')
        REPO_NAME = input("Enter the Github repository name: ")

        # create install.bat/sh for compiling run.go
        run_py_content = r'''
import server

server.main()
                '''
        bash_install_script_content = r'''
#!/bin/bash
# filepath: /Users/tylerretzlaff/Desktop/Projects/SCOPS2_LAN/install.sh

# Set repository owner and name
REPO_OWNER="'''+REPO_OWNER+r'''"
REPO_NAME="'''+REPO_NAME+r'''"

# GitHub API URL to fetch the latest release
API_URL="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"

# Use curl to fetch the latest release data and jq to parse JSON
DOWNLOAD_URL=$(curl -s "$API_URL" | jq -r '.assets[0].browser_download_url')
LATEST_RELEASE=$(curl -s "$API_URL" | jq -r '.assets[0].name')

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



# -- Install requirements.txt using Python --
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    sudo ./python/bin/python3.12 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements. Aborting."
        exit 1
    else
        echo "Requirements installed successfully."
    fi
else
    echo "requirements.txt not found."
fi

# Determine the OS
OS=$(uname)
CURRENT_DIR=$(pwd)

if [ "$OS" = "Linux" ]; then
    DESKTOP_FILE="$HOME/Desktop/'''+NAME+r'''.desktop"
    echo "Creating Linux desktop shortcut at $DESKTOP_FILE"
    cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name='''+NAME+r'''
Comment=Run '''+NAME+r'''
Exec=sudo ./python/bin/python3.12 $CURRENT_DIR/run.py
Icon=$CURRENT_DIR/'''+png+r'''
Terminal=false
Type=Application
Categories=Utility;
EOF
    chmod +x "$DESKTOP_FILE"

elif [ "$OS" = "Darwin" ]; then
    # macOS: create a minimal AppleScript-based app that launches run.py
    APP_PATH="$HOME/Desktop/'''+NAME+r'''.app"
    echo "Creating macOS desktop shortcut at $APP_PATH"
    mkdir -p "$APP_PATH/Contents/MacOS"
    cat <<EOF > "$APP_PATH/Contents/MacOS/'''+NAME+r'''"
#!/bin/bash
# Change directory to the folder containing run.py
cd "$CURRENT_DIR"
sudo ./python/bin/python3.12 run.py &
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
else
    echo "Unsupported OS: $OS. Please create a desktop shortcut manually."
fi

echo "Launching run.py..."
sudo ./python/bin/python3.12 run.py &
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
    ./python/windows/python.exe -m pip install -r requirements.txt
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
echo desktopShortcut.TargetPath = "python/windows/python.exe" >> CreateShortcut.vbs
echo desktopShortcut.Arguments = "run.py" >> CreateShortcut.vbs
echo desktopShortcut.WorkingDirectory = "%cd%" >> CreateShortcut.vbs
echo desktopShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo desktopShortcut.Save >> CreateShortcut.vbs
echo Set dirShortcut = objShell.CreateShortcut("%cd%\\'''+ NAME +r'''.lnk") >> CreateShortcut.vbs
echo dirShortcut.TargetPath = "python/windows/python.exe" >> CreateShortcut.vbs
echo dirShortcut.Arguments = "run.py" >> CreateShortcut.vbs
echo dirShortcut.WorkingDirectory = "%cd%" >> CreateShortcut.vbs
echo dirShortcut.IconLocation = "%~dp0'''+ ico +r'''" >> CreateShortcut.vbs
echo dirShortcut.Save >> CreateShortcut.vbs

:: Run the VBScript to create the shortcuts, then clean up
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo Shortcuts created successfully!
pause'''

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
        print(f'Files created successfully... now compress the folder into a zip file and upload it to github releases (matching the zip filename in the release file; {NAME}_{VERSION}.zip).')

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
    cli.add_command(create)
    cli.add_command(run)
    cli.add_command(compile)
    cli.add_command(cythonize)
    cli.add_command(gopherize)
    cli.add_command(assemble)
    cli.add_command(package)
    cli.add_command(distribute)
    cli.add_command(check)
    # cli.add_command(obfuscate)

    cli() #Run cli

if __name__ == '__main__':
    main()