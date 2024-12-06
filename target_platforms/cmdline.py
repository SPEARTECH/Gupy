from . import base
import os
import shutil
import platform
import sys

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
    ##Running checks on python version
    version = '.'.join(sys.version.split(' ')[0].split('.')[:2])
    if float(version) < 3.0:
        raise Exception('Please use Python3+. Make sure you have created a virtual environment.')

@click.command()
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

        self.main_content = f'''
from {self.name} import {self.name}

def main():
    {self.name}.main()

if __name__ == "__main__":
    main()
'''

        self.folders = [
          f'cli',
        #   f'gupy_apps/{self.name}/cli/dev/python_modules',
        #   f'gupy_apps/{self.name}/cli/dev/cython_modules',
          ]
          
        self.files = {
            f'cli/__init__.py': self.init_content,
            f'cli/__main__.py': self.main_content,
            f'cli/{self.name}.py': self.index_content,
            }

    def create(self):
        import shutil
        # check if platform project already exists, if so, prompt the user
        if self.folders[0] in os.listdir('.'):
            while True:
                userselection = input(self.folders[0]+' already exists for the app '+ self.name +'. Would you like to overwrite the existing '+ self.folders[0]+' project? (y/n): ')
                if userselection.lower() == 'y':
                    userselection = input('Are you sure you want to recreate the '+ self.folders[0]+' project for '+ self.name +'? (y/n)')
                    if userselection.lower() == 'y':
                        print("Removing old version of project...")
                        shutil.rmtree(os.path.join(os.getcwd(), self.folders[0]))
                        print("Continuing app platform creation.")
                        break
                    elif userselection.lower() != 'n':
                        print('Invalid input, please type y or n then press enter...')
                        continue
                    else:
                        print('Aborting app platform creation.')
                        return
                elif userselection.lower() != 'n':
                    print('Invalid input, please type y or n then press enter...')
                    continue
                else:
                    print('Aborting app platform creation.')
                    return
        
        for folder in self.folders:
            os.mkdir(folder)
            print(f'created "{folder}" folder.')
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()

    def run(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'
        # assign current python executable to use
        cmd = sys.executable.split(delim)[-1]

        # os.system(f'{cmd} {name}/desktop/dev/server/server.py')
        os.system(f'{cmd} __main__.py')
        




