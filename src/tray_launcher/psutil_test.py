import argparse
import os
import time as _t

import psutil as _ps

# def view_children(id):
#     p = _ps.Process(id)
#     children = p.children()
#     for child_process in children:
#         print(child_process.pid, flush=True)

# parser = argparse.ArgumentParser(description='View child processes of a given pid.')
# parser.add_argument('integer', metavar='N', type=int, nargs='+',
#                     help='Parent process\' pid')

# args = parser.parse_args()

# view_children(args.integer[0])

ti = _t.time()
p = _ps.Process(os.getpid()).create_time()

lc_t = _t.localtime(p)
print(
    str(lc_t.tm_hour).zfill(2),
    str(lc_t.tm_min).zfill(2),
    str(lc_t.tm_sec).zfill(2),
)

lc_tt = _t.localtime(ti)
print(
    str(lc_tt.tm_hour).zfill(2),
    str(lc_tt.tm_min).zfill(2),
    str(lc_tt.tm_sec).zfill(2),
)

print("time: " + str(ti))
print("psutil: " + str(p))
