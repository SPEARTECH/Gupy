from . import base
import os

class Desktop(base.Base):
    index_content = '''
    <html</html>
    '''
    server_content = '''
    <html</html>
    '''

    def __init__(self, name):
        self.name = name
        self.folders = [f'{self.name}/desktop', f'{self.name}/server']
        self.files = {
            f'{self.name}/desktop/index.html': self.index_content,
            f'{self.name}/server/server.py': self.server_content
            }

    def create(self):
        for folder in self.folders:
            os.mkdir(folder)
            print(f'created "{folder}" folder.')
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')