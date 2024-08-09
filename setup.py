from setuptools import setup

setup(
    name='gupy',
    version='0.0.1',
    py_modules=['gupy'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        gupy=gupy:cli
    ''',
)