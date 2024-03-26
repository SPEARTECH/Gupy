from logging import exception
import click
import sys
import os
from target_platforms import *
# import apps

NAME=''
LANG=''
TARGETS=[]
WEB=False
API=False

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
        ['desktop', 'mobile', 'pwa', 'website', 'api'], 
        case_sensitive=False
        ),
    multiple=True, 
    default=['desktop'], 
    help="Use this command for each platform you intend to target (ie. -t desktop -t mobile)"
    )
@click.option(
    '--lang',
    '-l',
    required=True,
    help='Language: "Py" or "Go"'
    )
def create(name,target_platform,lang):
    NAME=name #Assigning project name
    LANG=lang
    WEB=False
    API=False
    if LANG.lower() != 'py' and LANG.lower() != 'go':
        print(f'Incorrect option for --lang/-l\n Indicate "py" or "go" (Python/Golang)')
        return

    for target in target_platform: #Assigning target platforms
        TARGETS.append(target)

    if 'website' in TARGETS: #Value assignment for creating Django Project is applicable
        WEB=True

    if 'api' in TARGETS: #Value assignment for creating API Django Project is applicable
        API=True

    confirmation = click.confirm(f'''
Creating project with the following settings:
Project Name={NAME}
Targets={TARGETS}

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

    if 'mobile' in TARGETS: #create files/folder structure for mobile app if applicable
        mobile.Mobile(NAME).create()

    if 'pwa' in TARGETS: #create files/folder structure for pwa app if applicable
        pwa.Pwa(NAME).create()

    if WEB == True: #create files/folder for django project if applicable
        website.Website(NAME,LANG).create()

    if API == True: #install and create modifications to django project for api usage if applicable
        api.Api(NAME,LANG).create()

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
        ['desktop', 'mobile', 'pwa', 'website', 'api'], 
        case_sensitive=False
        ),
    required=True,
    multiple=False, 
    default=['desktop'], 
    help="Select the app platform you intend to run (ie. -t desktop)"
    )
@click.option(
    '--lang',
    '-l',
    required=True,
    help='Language: "Py" or "Go"'
    )
def run(name,target_platform,lang):
    NAME=name
    TARGET=target_platform
    LANG=lang
    if os.path.exists(f"apps/{NAME}"):
        if os.path.exists(f"apps/{NAME}/{TARGET}"):
            if TARGET == 'desktop':
                app_obj = desktop.Desktop(NAME,LANG)
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
    print('Printing apps in apps/ directory...\n')
    count = 0
    for item in os.listdir('apps/'):
        if item != '__pycache__':
            print(item)
            count += 1

    if count == 0:
        print('No apps created...\nTry "python ./r-cli.py create <commands>" to get started.')

    print('\n')


    
# @click.command()
# @click.option(
#     '--name',
#     '-n',
#     required=True,
#     help='Name of project'
#     )
# @click.option(
#     '--service',
#     '-s',
#     required=True,
#     type=click.Choice(
#         ['desktop', 'mobile', 'pwa', 'website'], 
#         case_sensitive=False
#         ),
#     multiple=False, 
#     help="Select which server to run"
# )
# def serve(name, service):
#     NAME=name #Assigning project name
#     if service.lower() == 'desktop':
#         desktop.Desktop(NAME).serve(NAME)
#     elif service.lower() == 'mobile':
#         mobile.Mobile(NAME).serve(NAME)
#     elif service.lower() == 'pwa':
#         pwa.Pwa(NAME).serve(NAME)
#     elif service.lower() == 'website':
#         website.Website(NAME).serve(NAME)

if __name__ == '__main__':
    cli.add_command(create) #Add command for cli
    cli.add_command(run) #Add command for cli
    cli.add_command(list)
    cli() #Run cli

