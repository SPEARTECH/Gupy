from logging import exception
import click
import sys
import os
from target_platforms import *
import platform
import chardet
import subprocess
import shutil

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
        elif 'pwa' in dir_list:
            TARGET='pwa'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
        elif 'website' in dir_list:
            TARGET='website'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
        elif 'cli' in dir_list:
            TARGET='cli'
            change_dir(dir_list,TARGET)
            NAME=os.path.dirname(os.getcwd()).split('\\')[-1]
        else:
            print(f'Error: No target platform folder found. Change directory to your app folder and use the create command (ex. cd <path to app>).')
            return

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

def check_golang_installed():
    """Check if Go is installed by trying to run 'go version'."""
    try:
        subprocess.run(["go", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Golang is already installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Golang is not installed.")
        return False

@click.command()
def install_go():
    if not check_golang_installed():
        """Install Go by downloading and running the installer based on the OS."""
        print("Installing Golang...")

        if sys.platform == "win32":
            # Windows installation (assumes curl is available)
            url = "https://golang.org/dl/go1.18.3.windows-amd64.msi"
            installer_file = "go_installer.msi"
            subprocess.run(["curl", "-o", installer_file, url], check=True)
            subprocess.run(["msiexec", "/i", installer_file, "/quiet", "/norestart"], check=True)
        elif sys.platform == "darwin":
            # macOS installation
            url = "https://golang.org/dl/go1.18.3.darwin-amd64.pkg"
            installer_file = "go_installer.pkg"
            subprocess.run(["curl", "-o", installer_file, url], check=True)
            subprocess.run(["sudo", "installer", "-pkg", installer_file, "-target", "/"], check=True)
        elif sys.platform == "linux":
            # Linux installation
            url = "https://golang.org/dl/go1.18.3.linux-amd64.tar.gz"
            tar_file = "go_installer.tar.gz"
            subprocess.run(["curl", "-o", tar_file, url], check=True)
            subprocess.run(["sudo", "tar", "-C", "/usr/local", "-xzf", tar_file], check=True)

            # Add Go to PATH
            go_path = "/usr/local/go/bin"
            bashrc_path = os.path.expanduser("~/.bashrc")
            with open(bashrc_path, "a") as bashrc:
                bashrc.write(f"\nexport PATH=$PATH:{go_path}\n")
            subprocess.run(["source", bashrc_path], shell=True, check=True)
        else:
            raise Exception(f"Platform {sys.platform} is not supported for Go installation.")

@click.command()
def distribute():
    try:
        # add project folder if not already created
        # move files+folders into project folder if just created
        # detect python version in pyd files
        # package latest python if not selected - make python folder with windows/mac/linux
        # install requirements with new python location
        # create go file for starting entry script for current os
        # compile go file
        # create run.sh for entry script
        # create run.bat for entry script
        pass
    except Exception as e:
        print('Error: '+str(e))
        return

@click.command()
@click.option(
    '--file',
    '-f',
    required=True,
    multiple=True, 
    default=[], 
    help='Select a single javascript file to obfuscate or select multiple (ie. -f view1.html -f view2.html).'
    )
def obfuscate():
    try:
        # for each file, obfuscate javascript (test with html file + vue options api - select lib to do this)
        pass
    except Exception as e:
        print('Error: '+str(e))
        return


def main():
    cli.add_command(create) #Add command for cli
    cli.add_command(run) #Add command for cli
    cli.add_command(compile)
    cli.add_command(cythonize)
    cli.add_command(gopherize)
    cli.add_command(assemble)
    cli.add_command(package)
    cli.add_command(install_go)
    cli.add_command(distribute)
    cli.add_command(obfuscate)

    cli() #Run cli

if __name__ == '__main__':
    main()