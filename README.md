# tray-launcher

[![Python: 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://docs.python.org/3.7/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI: tray-launcher](https://img.shields.io/pypi/v/tray-launcher)](https://pypi.org/project/tray-launcher/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A launcher that resides in the Windows taskbar for managing .bat scripts.

<img src="tray_launcher_at_work.png" width="620" height="410">
<img src="tray_launcher_at_work(2).png" width="620" height="410">
<img src="tray_launcher_at_work(3).png" width="620" height="410">

## Installation

*tray-launcher* can be installed with `pip install tray-launcher`. 

**Note**: *tray launcher* only works on Windows. 

## Usage

*tray launcher* comes with a command-line interface. Use `launcher -h` to learn more.

To get started, run `launcher run`, and a small icon will show on the taskbar.

Before running any scripts from *tray launcher*, they need to be loaded. This can be done by clicking the option **Load New Script(s)** in the context menu. Alternatively, run `launcher load [full path to the script]`. Only *.bat* files are accepted.

To run a script, select it in the **Start a Script** submenu from the context menu, or click **View All** to see all loaded scripts from a file dialogue, or run `launcher start [script name]`.

*tray launcher* listens to port `127.0.0.1:7686`. If this port is not available, the command line interface will not work. To fix this, create a new environment variable named `TRAY_LAUNCHER_PORT` in the control panel and set its value to an available port number.

Loggings of *tray launcher* and all scripts will be saved under `%USERPROFILE%\.tray_launcher\logs`.

In case of *tray launcher* crashing, scripts started via *tray launcher* will NOT be terminated.

There is an expected delay when executing "launcher run".
