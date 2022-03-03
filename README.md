# tray-launcher

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://docs.python.org/3.7/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
![Alt text](https://img.shields.io/badge/version-0.2.5-informational)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A launcher that resides in the Windows task bar for managing .bat scripts.

## Installation

*tray-launcher* can be installed with `pip install -i https://test.pypi.org/simple/ tray-launcher`.

## Usage

To start the *tray launcher*, first make sure you are in the Python environment variable where *tray-launcher* is installed. Then, running `launcher run` will show a small icon in the taskbar.

The *tray launcher* comes with a command line interface. Use `launcher -h` to learn more.

Before running any scripts from the tray launcher, they need to be loaded. This can be done by clicking the option **Load New Script(s)** in the contextmenu. Alternatively, paste scripts under `%USERPROFILE%\.tray_launcher\scripts`. Only *.bat* files are accepted.

To run a script, select it in the **Start a Script** submenu from the contextmenu, or click "View All" to see all loaded scripts in a file dialogue. 

Loggings of the *tray launcher* and the scripts you run will be saved under `%USERPROFILE%\.tray_launcher\logs`.

The *tray launcher* will list all scripts you started and are currently running. Move the cursor over to view more actions.

## Notes

1. The *tray launcher* only works on Windows. 

2. The *tray launcher* listens to `127.0.0.1:7686`. If this port is not available, the command line interface will not work. You need to go to control panel, create a new environment variable named `TRAY_LAUNCHER_PORT` and set its value to a port number that is available on your device.

3. If the *tray launcher* crashes, scripts started via the *tray launcher* will NOT be terminated.

4. There will be an expected delay when you run "launcher run".
