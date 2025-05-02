from . import base
import os
import shutil
import platform
import sys
from colorama import Fore, Style
import click

class Etl(base.Base):
    script_content = r'''
#!/usr/bin/env python
# coding: utf-8

# In[1]:
pip install --upgrade pip
pip install gophers

# In[2]:
import gophers as gf

# In[3]:
json = [{"hello":"gopher"}]
gf = gf.read_json(json)
gf.show()

# In[4]:
print("Running ETL")


'''

    def __init__(self, name, lang=''):
        self.name = name
        self.lang = lang

        self.folders = [
          f'etl',
        #   f'gupy_apps/{self.name}/cli/dev/python_modules',
        #   f'gupy_apps/{self.name}/cli/dev/cython_modules',
          ]
        if self.lang == 'py':
            self.files = {
                f'etl/{self.name}.py': self.script_content,
                }
        else:
            self.script_content = '''
package main

import (
    gf "gophers"
)

func main(){
    var json string
    json = [{"hello":"gopher"}]
    gf = gf.read_json(json)
    gf.show()
}
            '''
            self.files = {
                f'etl/main.go': self.script_content,
                }
    def create(self):
        import shutil
        # check if platform project already exists, if so, prompt the user
        if self.folders[0] in os.listdir('.'):
            while True:
                userselection = input(self.folders[0]+' already exists for the app '+ self.name +'. Would you like to overwrite the existing '+ self.folders[0]+' project? (y/n): ')
                if userselection.lower() == 'y':
                    click.echo(f'{Fore.RED}Are you sure you want to recreate the '+ self.folders[0]+' project for '+ self.name +f'? (y/n){Style.RESET_ALL}')
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
            # Get the directory of the current file
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Construct the path to the target file
            requirements_directory = os.path.join(os.path.dirname(current_directory), 'requirements.txt')       
            
            shutil.copy(requirements_directory, f'etl/requirements.txt')
        else:
            os.chdir('etl')
            os.system(f'go mod init example/{self.name}')
            os.system(f'go get https://www.github.com/speartech/gophers.git')
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
        if os.path.exists(f'{self.name}.py'):
            os.system(f'{cmd} {self.name}.py')
        elif os.path.exists(f'main.go'):
            os.system(f'go run main.go')
        else:
            click.echo(f'{Fore.RED}No entry file found of "{self.name}.py" or "main.go"{Style.RESET_ALL}')
        
    def distribute(self, system, folder, VERSION):
        # create stackscript code
        pass


