from logging import exception
import click
import sys
import os
from target_platforms import *

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
    LANG=language
    if '-' in NAME:
        print('Error: Invalid character of "-" in app name. Rename your app to '+ NAME.replace('-','_') +'.')
        return
    elif '.' in NAME:
        print('Error: Invalid character of "." in app name. Rename your app to '+ NAME.replace('.','_') +'.')
        return
    if not LANG and 'pwa' not in target_platform and 'website' not in target_platform:
        print("Error: Option '-l/--language' is required for ['desktop', 'cli', 'api'] targets.")
        return
    elif LANG and LANG.lower() != 'py' and LANG.lower() != 'go':
        print(f'Incorrect option for --lang/-l\n Indicate "py" or "go" (Python/Golang)')
        return
    elif not LANG and target_platform == 'pwa':
        LANG = 'javascript'
    elif not LANG and target_platform == 'website':
        LANG = 'python'

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
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'pwa', 'website', 'cli', 'api', 'mobile'], 
        case_sensitive=False
        ),
    required=True,
    multiple=False, 
    default=['desktop'], 
    help="Select the app platform you intend to run (ie. -t desktop)"
    )
def run(target_platform):
    # check if name is in path anywhere...
    # check if target-platform folder exists in path
    # overwrite prompt if yes
    # create name/target-platform folder then create files within it
    TARGET=target_platform
    if 'desktop' in dir_list or 'desktop' in os.listdir('.'):
        TARGET='desktop'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
        app_obj = desktop.Desktop(NAME)
        app_obj.run(NAME)
    elif 'pwa' in dir_list or 'pwa' in os.listdir('.'):
        TARGET='pwa'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
        app_obj = pwa.Pwa(NAME)
        app_obj.run(NAME)
    elif 'website' in dir_list or 'website' in os.listdir('.'):
        TARGET='website'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
        app_obj = website.Website(NAME)
        app_obj.run(NAME)
    elif 'cli' in dir_list or 'cli' in os.listdir('.'):
        TARGET='cli'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
        app_obj = cmdline.CLI(NAME)
        app_obj.run(NAME)
    elif TARGET == 'desktop' or TARGET == 'pwa' or TARGET == 'website' or TARGET == 'cli':
        print(f'{NAME} app does not have a project platform of {TARGET}. Use the create command and try again.')
    else:
        print(f'{TARGET} is not yet enabled for this feature...')

# @click.command()
# def list():
#     # apps.Apps.getapps()
#     # for item in os.listdir('gupy_apps/'):
#     #     print(item)
#     print(f'Printing apps in {os.path.abspath("./apps")} directory...\n')
#     count = 0
#     for item in os.listdir('gupy_apps/'):
#         if item != '__pycache__':
#             print(item)
#             count += 1

#     if count == 0:
#         print('No apps created...\nTry "python ./gupy.py create <commands>" to get started.')

#     print('\n')

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
                os.system(f'go mod tidy')
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
        os.system(f'go build -o {os.path.splitext(file)[0]}.so -buildmode=c-shared {item} ')

@click.command()
@click.option(
    '--file',
    '-f',
    required=False,
    help='Select a single file to assemble or select multiple (ie. -f module1.go -f module2.go).'
    )
def assemble(file):
    dir_list = os.getcwd().split('\\')
    def change_dir(dir_list,target):
        if target in dir_list: 
            index = dir_list.index(target)
            chdir_num = len(dir_list) - index
            os.chdir('../'*chdir_num)
        elif target in os.listdir('.'):
            os.chdir(target)
    # detect the platform in the current directory or parent directories and then change directory to its root for operation
    if 'desktop' in dir_list or 'desktop' in os.listdir('.'):
        TARGET='desktop'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
    elif 'pwa' in dir_list or 'pwa' in os.listdir('.'):
        TARGET='pwa'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
    elif 'website' in dir_list or 'website' in os.listdir('.'):
        TARGET='website'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
    else:
        print(f'Error: No target platform folder of {TARGET} found. Change directory to your app and try again (ex. cd <path to app>).')
        return

    if TARGET == 'desktop':
        app_obj = desktop.Desktop(NAME)
        app_obj.assemble(NAME)
    elif TARGET == 'website':
        app_obj = website.Website(NAME)
        app_obj.assemble(NAME)
    elif TARGET == 'pwa':
        app_obj = pwa.Pwa(NAME)
        app_obj.assemble(NAME)
    else:
        print(TARGET+' platform not enabled for assembly. Change directory to your app root folder with desktop, pwa, or website platforms (ex. cd <path to app>/<platform>).')

@click.command()
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'cli'], 
        case_sensitive=False
        ),
    required=True,
    multiple=False, 
    default=[], 
    help="Select the app platform you intend to run (ie. -t desktop)"
    )
def package():
    dir_list = os.getcwd().split('\\')
    def change_dir(dir_list,target):
        if target in dir_list: 
            index = dir_list.index(target)
            chdir_num = len(dir_list) - index
            os.chdir('../'*chdir_num)
        elif target in os.listdir('.'):
            os.chdir(target)
    # detect the platform in the current directory or parent directories and then change directory to its root for operation
    if 'desktop' in dir_list or 'desktop' in os.listdir('.'):
        TARGET='desktop'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
    elif 'cli' in dir_list or 'cli' in os.listdir('.'):
        TARGET='cli'
        change_dir(dir_list,TARGET)
        NAME=os.path.dirname(os.getcwd())
    else:
        print(f'Error: No target platform folder of {TARGET} found. Change directory to your app folder and use the create command (ex. cd <path to app>).')
        return

    toml_content = '''
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

[project.urls]
Homepage = "https://github.com/pypa/sampleproject"
Issues = "https://github.com/pypa/sampleproject/issues"

# Specify the directory where your Python package code is located
[tool.hatch.build.targets.sdist]
include = ["*"]

[tool.hatch.build.targets.wheel]
packages = ["*"]
'''
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

    print('changing directory...')
    os.chdir('cli/')
    print('checking for README.md...')
    if 'README.md' not in os.listdir('.'):
        f = open(file, 'x')
        f.write(readme_content)
        print(f'created "{file}" file.')
        f.close()
    print('checking for LICENSE...')
    if 'LICENSE' not in os.listdir('.'):
        f = open(file, 'x')
        f.write(license_content)
        print(f'created "{file}" file.')
        f.close()
    print('checking for pyproject.toml...')
    if 'pyproject.toml' not in os.listdir('.'):
        f = open(file, 'x')
        f.write(toml_content)
        print(f'created "{file}" file.')
        f.close()
        print('pyproject.toml created with default values. Modify it to your liking and rerun the package command.')
        return

    os.system(f'{cmd} -m build')


def main():
    cli.add_command(create) #Add command for cli
    cli.add_command(run) #Add command for cli
    # cli.add_command(list)
    cli.add_command(compile)
    cli.add_command(cythonize)
    cli.add_command(gopherize)
    cli.add_command(assemble)
    cli() #Run cli

if __name__ == '__main__':
    main()