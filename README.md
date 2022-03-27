# tray-launcher

[![Python: 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://docs.python.org/3.7/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI: tray-launcher](https://img.shields.io/pypi/v/tray-launcher)](https://pypi.org/project/tray-launcher/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A launcher that resides in the Windows taskbar for managing .bat scripts.

## Installation

*tray-launcher* can be installed with `pip install tray-launcher`.

## Usage

To get started, `launcher run` and a small icon in the taskbar.

The *tray launcher* comes with a command-line interface. Use `launcher -h` to learn more.

Before running any scripts from the tray launcher, they need to be loaded. This can be done by clicking the option **Load New Script(s)** in the context menu. Alternatively, paste scripts under `%USERPROFILE%\.tray_launcher\scripts`. Only *.bat* files are accepted.

To run a script, select it in the **Start a Script** submenu from the context menu, or click "View All" to see all loaded scripts in a file dialogue. 

Loggings of the *tray launcher* and the scripts you run will be saved under `%USERPROFILE%\.tray_launcher\logs`.

*tray launcher* will list all scripts you started and are currently running. Move the cursor over to view more actions.

## Notes

1. *tray launcher* only works on Windows. 

2. *tray launcher* listens to `127.0.0.1:7686`. If this port is not available, the command line interface will not work. You need to go to the control panel, create a new environment variable named `TRAY_LAUNCHER_PORT`, and set its value to a port number that is available on your device.

3. If *tray launcher* crashes, scripts started via the *tray launcher* will NOT be terminated.

4. There will be an expected delay when executing "launcher run".

## Screenshot
![tray-launcher](tray_launcher_at_work.png)
