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
        ['desktop', 'pwa', 'website', 'cli'], 
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
def create(name,target_platform,language):
    NAME=name #Assigning project name
    LANG=language

    if not LANG and target_platform != ('pwa',):
        print("Error: Option '-l/--language' is required for ['desktop', 'cli'] targets.")
        return
    elif LANG and LANG.lower() != 'py' and LANG.lower() != 'go':
        print(f'Incorrect option for --lang/-l\n Indicate "py" or "go" (Python/Golang)')
        return
    elif not LANG:
        LANG = 'javascript'

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
    obj.create_project_folder() #Create Project folder

    if 'desktop' in TARGETS: #create files/folder structure for desktop app if applicable
        desktop.Desktop(NAME,LANG).create()

    if 'pwa' in TARGETS: #create files/folder structure for pwa app if applicable
        pwa.Pwa(NAME).create()

    if 'website' in TARGETS: #create files/folder for django project if applicable
        website.Website(NAME).create()

    if 'cli' in TARGETS: #create files/folder structure for cli app if applicable
        cmdline.CLI(NAME,LANG).create()

@click.command()
@click.option(
    '--name',
    '-n',
    required=True,
    help='Name of app'
    )
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'pwa', 'website', 'cli'], 
        case_sensitive=False
        ),
    required=True,
    multiple=False, 
    default=['desktop'], 
    help="Select the app platform you intend to run (ie. -t desktop)"
    )
def run(name,target_platform):
    NAME=name
    TARGET=target_platform
    if os.path.exists(f"apps/{NAME}"):
        if os.path.exists(f"apps/{NAME}/{TARGET}"):
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
        print(f'{NAME} folder does not exist. Try listing all apps with "python ./r-cli.py list"')

@click.command()
def list():
    # apps.Apps.getapps()
    # for item in os.listdir('apps/'):
    #     print(item)
    print(f'Printing apps in {os.path.abspath("./apps")} directory...\n')
    count = 0
    for item in os.listdir('apps/'):
        if item != '__pycache__':
            print(item)
            count += 1

    if count == 0:
        print('No apps created...\nTry "python ./gupy.py create <commands>" to get started.')

    print('\n')

@click.command()
@click.option(
    '--name',
    '-n',
    required=True,
    help='Name of app'
    )
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'pwa', 'website', 'cli'], 
        case_sensitive=False
        ),
    required=True,
    multiple=False, 
    default=['desktop'], 
    help="Select the app platform you intend to run (ie. -t desktop)"
    )
def compile(name,target_platform):
    NAME=name
    TARGET=target_platform
    if os.path.exists(f"apps/{NAME}"):
        if os.path.exists(f"apps/{NAME}/{TARGET}"):
            if TARGET == 'desktop':
                app_obj = desktop.Desktop(NAME)
                app_obj.compile(NAME)
            elif TARGET == 'cli':
                app_obj = cmdline.CLI(NAME)
                app_obj.compile(NAME)
            else:
                print('other platforms not enabled for this feature yet...')
        else:
            print(f'{NAME} app does not have a target platform of {TARGET}.')
    else:
        print(f'{NAME} folder does not exist. Try listing all apps with "python ./gupy.py list"')

@click.command()
@click.option(
    '--name',
    '-n',
    required=True,
    help='Name of app'
    )
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'pwa', 'website', 'cli'], 
        case_sensitive=False
        ),
    required=True,
    multiple=False, 
    default=['desktop'], 
    help="Select the app platform you intend to run (ie. -t desktop)"
    )
def cythonize(name,target_platform):
    NAME=name
    TARGET=target_platform
    if os.path.exists(f"apps/{NAME}"):
        if os.path.exists(f"apps/{NAME}/{TARGET}"):
            if TARGET == 'desktop':
                app_obj = desktop.Desktop(NAME)
                app_obj.cythonize(NAME)
            elif TARGET == 'website':
                app_obj = website.Website(NAME)
                app_obj.cythonize(NAME)
            elif TARGET == 'cli':
                app_obj = cmdline.CLI(NAME)
                app_obj.cythonize(NAME)
            else:
                print('other platforms not enabled for this feature yet...')
        else:
            print(f'{NAME} app does not have a target platform of {TARGET}.')
    else:
        print(f'{NAME} folder does not exist. Try listing all apps with "python ./gupy.py list"')

@click.command()
@click.option(
    '--name',
    '-n',
    required=True,
    help='Name of app'
    )
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'pwa', 'website', 'cli'], 
        case_sensitive=False
        ),
    required=True,
    multiple=False, 
    default=['desktop'], 
    help="Select the app platform you intend to run (ie. -t desktop)"
    )
def gopherize(name,target_platform):
    NAME=name
    TARGET=target_platform
    if os.path.exists(f"apps/{NAME}"):
        if os.path.exists(f"apps/{NAME}/{TARGET}"):
            if TARGET == 'desktop':
                app_obj = desktop.Desktop(NAME)
                app_obj.gopherize(NAME)
            elif TARGET == 'website':
                app_obj = website.Website(NAME)
                app_obj.gopherize(NAME)
            elif TARGET == 'cli':
                app_obj = cmdline.CLI(NAME)
                app_obj.gopherize(NAME)
            elif TARGET == 'pwa':
                app_obj = pwa.Pwa(NAME)
                app_obj.gopherize(NAME)
            else:
                print('other platforms not enabled for this feature yet...')
        else:
            print(f'{NAME} app does not have a target platform of {TARGET}.')
    else:
        print(f'{NAME} folder does not exist. Try listing all apps with "python ./gupy.py list"')


if __name__ == '__main__':
    cli.add_command(create) #Add command for cli
    cli.add_command(run) #Add command for cli
    cli.add_command(list)
    cli.add_command(compile)
    cli.add_command(cythonize)
    cli.add_command(gopherize)
    cli() #Run cli

