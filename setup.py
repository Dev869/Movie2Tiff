from setuptools import setup

APP = ['tifdrop.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'tkinterdnd2', 'tkdnd'],  # List any other dependencies here
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)