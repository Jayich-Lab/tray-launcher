# tray-launcher

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://docs.python.org/3.7/)

A launcher resided in the task bar for managing .bat scripts.

## Installation

*tray-launcher* can be installed by running `pip install -i https://test.pypi.org/simple/ tray-launcher`. It requires Python 3.7+ to run.

## Usage

To start the *tray launcher*, first make sure you are in the Python environment variable where *tray-launcher* is installed. Then, running `tray-launcher` will show a small icon in the taskbar.

Before you run any scripts from the tray launcher, you need to load them. This can be done by clicking the option **Load New Script(s)** in the contextmenu. Alternatively, you could also paste your scripts under `%USERPROFILE%\.tray_launcher\scripts`. Only *.bat* files are accepted.

To run a script, select it in the **Start a Script** submenu from the contextmenu, or click "View All" to see all loaded scripts in a file dialogue. 

Loggings of the *tray launcher* and the scripts you run will be saved under `%USERPROFILE%\.tray_launcher\logs`.

The *tray launcher* will list all scripts you started and are currently running. Move the cursor over to view more actions.

***New***: Now you can access tray launcher with cmd! `launcher -h` to see how our CLI works.

## Warnings

The tray launcher is listening to `host: 127.0.0.1`, `port: 7686`. If this port is not available, the command line interface will not work. You need to go to control panel, create a new *system* environment variable named `TRAY_LAUNCHER_PORT` and set its value to a port number that is available on your device.
