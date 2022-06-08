import click
import sys
sys.path.insert(0,r'C:\Users\stephen.retzlaff\OneDrive - caci_caci\Desktop\Projects\Raptor-CLI\raptor-cli')
from target_platforms import *

NAME=''
TARGETS=[]
DJANGO=False
API=False

@click.group()
def cli():
    pass

@click.command()
@click.option(
    '--name',
    '-n',
    required=True,
    help='Name of your project'
    )
@click.option(
    '--target-platform',
    '-t',
    type=click.Choice(
        ['desktop', 'mobile', 'pwa', 'website'], 
        case_sensitive=False
        ),
    multiple=True, 
    default=['desktop'], 
    help="Use this command for each platform you intend to target (ie. -t desktop -t mobile)"
    )
def create(name,target_platform):
    NAME=name #Assigning project name
    for target in target_platform: #Assigning target platforms
        TARGETS.append(target)

    if 'desktop' in TARGETS:
        DJANGO=False
        API=False

    if 'website' in TARGETS: #Value assignment for creating Django Project is applicable
        DJANGO=True
        API=False

    if ('mobile' or 'pwa') in TARGETS: #Value assignment for creating API Django Project is applicable
        DJANGO=True
        API=True
    confirmation = click.confirm(f'''
Creating project with the following settings:
Project Name={NAME}
Targets={TARGETS}
Django Project={DJANGO}
Django API={API}

Confirm? 
''', default=True, show_default=True
) #Confirm user's settings

    if confirmation == False: #Exit if settings are incorrect
        click.echo('Exiting...')
        return

    obj = base.Base(NAME)
    obj.create_project_folder() #Create Project folder

    if 'desktop' in TARGETS: #create files/folder structure for desktop app if applicable
        desktop.Desktop(NAME).create()

    if 'mobile' in TARGETS: #create files/folder structure for mobile app if applicable
        mobile.Mobile(NAME).create()

    if 'pwa' in TARGETS: #create files/folder structure for pwa app if applicable
        pwa.Pwa(NAME).create()

    if DJANGO == True: #create files/folder for django project if applicable
        website.Website(NAME).create()

    if API == True: #install and create modifications to django project for api usage if applicable
        api.Api().create()

if __name__ == '__main__':
    cli.add_command(create) #Add command for cli
    cli() #Run cli