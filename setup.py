
import os
from setuptools import setup, find_packages


from pyrometer import APPLICATION_VERSION, AUTHOR_NAME, AUTHOR_EMAIL


#
setup(
    # info
    name='pyrometer',
    description='Specral pyrometer to estimate temperature of heated body.',
    license='MIT',

    # version
    version=APPLICATION_VERSION,

    # author details
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,

    # setup directories
    packages=find_packages(),
    # package_dir={
    #     '': 'pyrometer',
    # },
    # package_data={
    #     '': [],
    # },

    # requires
    install_requires=['PySide6', 'spectrumlab @ git+https://github.com/Exinker/spectrumlab.git'],
    python_requires='>=3.10',
)
