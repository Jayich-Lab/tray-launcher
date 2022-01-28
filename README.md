# tray-launcher

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://docs.python.org/3.7/)

A launcher resided in the task bar for managing .bat scripts.

## Installation

*tray-launcher* can be installed by running `pip install -i https://test.pypi.org/simple/ tray-launcher==0.1.4`. It requires Python 3.7+ to run.

In the near future when it's up in PyPi, you should be able to install it by `pip install tray-launcher`. 

## Usage

To start the *tray launcher*, first make sure you are in `code3` or `artiq`. Then, running `tray-launcher` will show a small icon in the taskbar.

Before you run any scripts from the tray launcher, you need to load them. This can be done by clicking the option **Load New Script(s)** in the contextmenu. Alternatively, you could also paste your scripts under `C:\Users\scientist\tray_launcher\available_scripts`. Only *.bat* files are accepted.

To run a script, select it in the **Start a Script** submenu from the contextmenu, or click "View All" to see all loaded scripts in a file dialogue. 

Loggings of the *tray launcher* and the scripts you run will be saved under `C:\Users\scientist\tray_launcher\logs`.

The *tray launcher* will list all scripts you started and are currently running. Move the cursor over to view more actions.
