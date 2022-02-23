# tray-launcher

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://docs.python.org/3.7/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

A launcher resided in the task bar for managing .bat scripts.

## Installation

*tray-launcher* can be installed with `pip install -i https://test.pypi.org/simple/ tray-launcher`.

## Usage

To start the *tray launcher*, first make sure you are in the Python environment variable where *tray-launcher* is installed. Then, running `tray-launcher` will show a small icon in the taskbar.

*tray launcher* comes with a CLI. Enter `launcher -h` to learn how it works.

Before you run any scripts from the tray launcher, you need to load them. This can be done by clicking the option **Load New Script(s)** in the contextmenu. Alternatively, you could also paste your scripts under `%USERPROFILE%\.tray_launcher\scripts`. Only *.bat* files are accepted.

To run a script, select it in the **Start a Script** submenu from the contextmenu, or click "View All" to see all loaded scripts in a file dialogue. 

Loggings of the *tray launcher* and the scripts you run will be saved under `%USERPROFILE%\.tray_launcher\logs`.

The *tray launcher* will list all scripts you started and are currently running. Move the cursor over to view more actions.

## Notes

1. The *tray launcher* listens to `127.0.0.1:7686`. If this port is not available, the command line interface will not work. You need to go to control panel, create a new environment variable named `TRAY_LAUNCHER_PORT` and set its value to a port number that is available on your device.

2. If the *tray launcher* crashes, scripts started via the *tray launcher* will NOT be terminated.

3. There will be an expected delay when you run "launcher run".
