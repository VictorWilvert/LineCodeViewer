#!/usr/bin/env python

import os
from setuptools import setup

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

with open(f'{FILE_PATH}/requirements.txt') as file:
    requirements = list(file)

setup(
    name='LineCodeViewer',
    version='0.1',
    install_requires=requirements,
    packages=[

        'linecodeviewer',
        'linecodeviewer.imgs',
        'linecodeviewer.forms'
    ],
    package_dir={

        'linecodeviewer': 'src',
        'linecodeviewer.forms': 'forms',
        'linecodeviewer.imgs': 'imgs'
    },
    package_data={

        'linecodeviewer.forms': ['*.ui'],
        'linecodeviewer.imgs': ['*_rc.py'],
    },
    entry_points={

        'gui_scripts': [
            'linecodeviewer = linecodeviewer.mainwindow:main',
        ]
    }
)
