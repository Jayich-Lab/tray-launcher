import os
import signal
import subprocess
import time as _t
from pathlib import Path


USER_HOME = Path.home() / ".tray_launcher"
LOGS = USER_HOME / "logs"

t = _t.localtime(_t.time())
log_directory = LOGS / (
                str(t.tm_year) + "_" + str(t.tm_mon).zfill(2) + "_" + str(t.tm_mday).zfill(2)
            )
log_directory.mkdir(parents=True, exist_ok=True)

log_path = log_directory / "{}-{}_{}_{}.log".format(
            "time.bat_TEST",
            str(t.tm_hour).zfill(2),
            str(t.tm_min).zfill(2),
            str(t.tm_sec).zfill(2),
        )

try:
    outputs_file = open(log_path, "a")
except Exception as err:
    print(err + ": Failed to open/create a file for outputs")
    raise

print("File opened.")
subp = subprocess.Popen(
        "C:\\Users\\danhu\Desktop\\time.bat",
        encoding="utf-8",
        stdout=outputs_file,
        stderr=outputs_file,
        #creationflags=subprocess.CREATE_NO_WINDOW,
    )

print(subp.pid)

# wmic_ = subprocess.run(
#             "wmic process where (ParentProcessId={}) get ProcessId".format(
#                 str(subp.pid)
#             ),
#             encoding="utf-8",
#             stdout=subprocess.PIPE,
#             shell=True,
#         )

# for line in wmic_.stdout.split("\n"):
#     print(line)