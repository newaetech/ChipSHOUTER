#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'chipshouter',
    version = '1.0.0',
    description = "ChipSHOUTER EMFI API",
    author = "Colin O'Flynn",
    author_email = 'coflynn@newae.com',
    license = 'GPLv3',
    url = 'http://www.ChipSHOUTER.com',
    download_url='https://github.com/newaetech/chipshouter',
    packages = ['chipshouter',
                'chipshouter.console'
                ],
    scripts=['scripts/shouter-console.py'],
    install_requires = [
        'pyserial',
        'PyCRC',\
        'tqdm'
    ],
)
