import argparse 
from tray_launcher import tray_launcher_client

def get_parser():
    parser = argparse.ArgumentParser(prog="tray_launcher", description="Manage scripts with the tray launcher"
    )

    launcher = parser.add_subparsers(dest="launcher")
    launcher.required = True

    p_start = launcher.add_parser("start", help="Starts scripts")
    p_start.add_argument("start_script", type=str, nargs="*", metavar="script_stem", help="Start new script(s)")

    p_quit = launcher.add_parser("quit", help="Quit the tray launcher")
    p_quit.add_argument("quit_launcher", action="store_true", help="Quit the tray launcher")

    return parser

def main():
    args = get_parser().parse_args()

    if args.launcher == "quit":
        print("quit")

    if args.launcher == "start":
        print(args.launcher.quit_launcher)