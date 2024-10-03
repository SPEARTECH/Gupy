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

    if not LANG and target_platform != 'pwa' and target_platform != 'website' and target_platform != ('pwa', 'website'):
        print("Error: Option '-l/--language' is required for ['desktop', 'cli', 'api'] targets.")
        return
    elif LANG and LANG.lower() != 'py' and LANG.lower() != 'go':
        print(f'Incorrect option for --lang/-l\n Indicate "py" or "go" (Python/Golang)')
        return
    elif not LANG and target_platform == 'pwa':
        LANG = 'javascript'
    elif not LANG and target_platform == 'website':
        LANG = 'python'

    dir_list = os.getcwd().split('\\\\')
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
        pass
    
    if 'mobile' in TARGETS:
        pass

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
    if os.path.exists(f"{NAME}"):
        if os.path.exists(f"{NAME}/{TARGET}"):
            if TARGET == 'desktop':
                app_obj = desktop.Desktop(NAME)
                app_obj.run(NAME)
            elif TARGET == 'cli':
                app_obj = cmdline.CLI(NAME)
                app_obj.run(NAME)
            elif TARGET == 'website':
                app_obj = website.Website(NAME)
                app_obj.run(NAME)
            elif TARGET == 'pwa':
                app_obj = pwa.Pwa(NAME)
                app_obj.run(NAME)
            else:
                print('other platforms not enabled for this feature yet...')
        else:
            print(f'{NAME} app does not have a target platform of {TARGET}.')
    else:
        print(f'{NAME} folder does not exist. Try listing all apps with "python ./gupy.py list" or "python -m gupy list"')

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
    required=False,
    default=[''], 
    help="Select a single file to cythonize or keep blank to cythonize recursively from current directory (ie. -f script.py)."
    )
def cythonize(file):
    # files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if file == '':
        setup_content = '''
from distutils.core import setup
from Cython.Build import cythonize
import os

# Recursively find all Python files
def find_python_files(base_dir):
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                if file != "__init__.py" and file != "__main__.py" and file != "setup.py":
                    full_path = os.path.join(root, file)
                    python_files.append(full_path)
    return python_files

# find all python files recursively other than __init__.py __main__.py and setup.py
python_files = find_python_files(".")

setup(
    ext_modules=cythonize(python_files, compiler_directives={'language_level': "3"}),
)
'''
    else:
        if os.path.exists(file):
            setup_content = '''
from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("'''+file+'''", compiler_directives={'language_level': "3"}),
)
'''
        else:
            print('Error: '+file+' not found. Try again...')
            return

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

@click.command()
@click.option(
    '--file',
    '-f',
    required=False,
    help='Select a single file to gopherize or keep blank to gopherize recursively (excluding the go_wasm folder) from current directory (ie. -f main.go).'
    )
def gopherize(file):
    FILE=file
    # Recursively find all Python files
    def find_go_files(base_dir):
        files = []
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".go"):
                    full_path = os.path.join(root, file)
                    files.append(full_path)
        return files
    if not FILE:
        # os.system(f'go mod tidy')
        # find all go files recursively
        files = find_go_files(".")        
        # files = [f for f in glob.glob('*.go')]
    else:
        files = [FILE]

    for file in files:
        print(f'Building {file} file...')
        os.system(f'go build -o {os.path.splitext(file)[0]}.so -buildmode=c-shared {file} ')

@click.command()
@click.option(
    '--file',
    '-f',
    required=False,
    help='Select a single file to gopherize or keep blank to gopherize recursively (excluding the go_wasm folder) from current directory (ie. -f main.go).'
    )
def assemble(file):
    FILE=file
    dir_list = os.getcwd().split('\\\\')
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
    elif 'pwa' in dir_list or 'pwa' in os.listdir('.'):
        TARGET='pwa'
        change_dir(dir_list,TARGET)
    elif 'website' in dir_list or 'website' in os.listdir('.'):
        TARGET='website'
        change_dir(dir_list,TARGET)
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

def package():
    pass

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