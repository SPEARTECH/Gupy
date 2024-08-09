import os

class Base:
    project_folder = ''
    
    def __init__(self, name):
        self.project_folder = name
        self.platform = os.name #not needed at the moment (not using platform specific terminal commands)

    def create_project_folder(self): 
        #Create project folder
        if not os.path.exists('gupy_apps/'+self.project_folder):
            os.mkdir('gupy_apps/'+self.project_folder)
            print(f'created "{self.project_folder}" project folder.')
        else:
            print(f'"{self.project_folder}" already exists.')
        
