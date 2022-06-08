from . import base
import os

class Pwa(base.Base):
    index_content = '''
    
    '''

    def __init__(self, name):
        self.name = name
        self.folders = ['pwa']
        self.files = {
            '/pwa/index.html': self.index_content,
            }

    def create(self):
        for folder in self.folders:
            os.mkdir(folder)
            print('created "{folder}" folder.')
        
        for file in self.files:
            f = open(file, 'x')
            f.write()
            print(f'created "{file}" file.')