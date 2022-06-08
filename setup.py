from setuptools import setup

setup(
    name='r-cli',
    version='0.0.1',
    py_modules=['r-cli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        r-cli=r-cli:say_hello
    ''',
)