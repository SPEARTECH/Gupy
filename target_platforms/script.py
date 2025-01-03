from . import base
import os
import shutil
import platform
import sys

class Script(base.Base):
    script_content = '''
def main():
    print('Script run complete.')

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
          f'script',
        #   f'gupy_apps/{self.name}/cli/dev/python_modules',
        #   f'gupy_apps/{self.name}/cli/dev/cython_modules',
          ]
          
        self.files = {
            f'script/__init__.py': self.init_content,
            f'script/__main__.py': self.main_content,
            f'script/{self.name}.py': self.script_content,
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
        os.system(f'{cmd} {self.name}.py')
        




