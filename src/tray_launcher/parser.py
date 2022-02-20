import argparse 
from tray_launcher import tray_launcher_client

def create_parser():
    parser = argparse.ArgumentParser(
        prog="tray_launcher", description="Manage scripts with the tray launcher"
    )

    parser.add_argument(
        "-s", "--start", nargs="*", metavar="script_stem", type=str, help="Start new script(s)"
    )

    parser.add_argument(
        "-t",
        "--terminate",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Terminate the script specified",
    )

    parser.add_argument(
        "-L", "--list", action="store_true", help="List all loaded scripts"
    )

    parser.add_argument(
        "-l", "--list-current", action="store_true", help="List all currently running scripts"
    )

    parser.add_argument(
        "--load", nargs="*", metavar="script_path", type=str, help="Load some scripts"
    )

    parser.add_argument(
        "-r",
        "--restart",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Restart the script specified",
    )

    parser.add_argument(
        "--log",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="View log of the specified, currently running script. Show the log of the tray launcher application when the user calls launcher --log tray-launcher",
)

    parser.add_argument(
        "-f",
        "--front",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Bring the specified script to the foreground",
    )

    parser.add_argument("-q", "--quit", action="store_true", help="Quit the tray launcher")
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.load is not None:
        print("Loading {}.".format(args.load))
        tray_launcher_client.TrayLauncherClient("load", args.load)

    elif args.start is not None:
        print("Starting {}.".format(args.start))
        tray_launcher_client.TrayLauncherClient("start", args.start)

    elif args.log is not None:
        print("Showing log of {}.".format(args.log))
        tray_launcher_client.TrayLauncherClient("log", args.log)

    elif args.restart is not None:
        print("Restarting {}.".format(args.restart))
        tray_launcher_client.TrayLauncherClient("restart", args.restart)

    elif args.front is not None:
        print("Bringing {} to the foreground.".format(args.front))
        tray_launcher_client.TrayLauncherClient("front", args.front)

    elif args.terminate is not None:
        print("Terminating {}.".format(args.terminate))
        tray_launcher_client.TrayLauncherClient("terminate", args.terminate)

    elif args.list is True:
        print("Available scripts: ")
        tray_launcher_client.TrayLauncherClient("list", [])

    elif args.list_current is True:
        print("Currently running scripts: ")
        tray_launcher_client.TrayLauncherClient("list_current", [])

    elif args.quit is True:
        print("Quitting tray launcher.")
        tray_launcher_client.TrayLauncherClient("quit", [])


if __name__ == "__main__":
    main()