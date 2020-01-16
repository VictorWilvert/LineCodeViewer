#!/usr/bin/env python

import os
from setuptools import setup

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

with open(f'{FILE_PATH}/requirements.txt') as file:
    requirements = list(file)

RC_FILENAME = f'{FILE_PATH}/imgs/images_rc.py'

if not os.path.exists(RC_FILENAME):

    try:
        from PyQt5 import pyrcc_main
    except ImportError as err:
        raise Exception('Requires \'PyQt5\' package to run setup') from err

    if not pyrcc_main.processResourceFile([f'{FILE_PATH}/imgs/images.qrc'],
                                          RC_FILENAME, False):
        raise Exception('Error occurred creating resource file')

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
    },
    license='GPL-3.0'
)
