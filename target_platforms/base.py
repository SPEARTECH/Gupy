import os
import platform

class Base:
    project_folder = ''
    
    def __init__(self, name):
        self.project_folder = name
        # self.platform = os.name #not needed at the moment (not using platform specific terminal commands)

    def create_project_folder(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'
        #Create project folder
        dir_list = os.getcwd().split(delim)
        def change_dir(dir_list,name):
            if name in dir_list: 
                index = dir_list.index(name)
                chdir_num = len(dir_list) - index
                os.chdir('../'*chdir_num )
            elif name in os.listdir('.'):
                os.chdir(name)

        if self.project_folder in dir_list or self.project_folder in os.listdir('.'):
            print(f'"{self.project_folder}" already exists, changing directory to its root folder.')
            change_dir(dir_list,self.project_folder)
            print(f'Changed directory to {self.project_folder}')
        else:
            os.mkdir(self.project_folder)
            os.chdir(self.project_folder)
            print(f'Created "{self.project_folder}" project folder.')
            print(f'Changed directory to {self.project_folder}')
        
