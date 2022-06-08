from . import base
import os

class Website(base.Base):
    index_content = '''
    
    '''
    server_content = '''
    
    '''

    def __init__(self, name):
        self.name = name
        self.folders = ['desktop', 'server']
        self.files = {
            '/desktop/index.html': self.index_content,
            '/server/server.py': self.server_content
            }

    def create(self):
        os.system(f'django-admin startproject {self.name}')
        print('starting django project...')