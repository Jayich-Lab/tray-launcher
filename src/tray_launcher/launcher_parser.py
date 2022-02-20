import argparse

from tray_launcher import gui, tray_launcher_client


def get_parser():
    parser = argparse.ArgumentParser(
        prog="tray_launcher", description="Manage scripts with the tray launcher"
    )

    launcher = parser.add_subparsers(dest="launcher")
    launcher.required = True

    p_start = launcher.add_parser("start", help="Starts scripts")
    p_start.add_argument(
        "starting_scripts", type=str, nargs="*", metavar="script_stem", help="Scripts to be started"
    )

    launcher.add_parser("quit", help="Quits the tray launcher")

    p_terminate = launcher.add_parser("terminate", help="Terminates scripts")
    p_terminate.add_argument(
        "terminating_scripts",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Scripts to be terminated",
    )

    launcher.add_parser("run", help="Runs the tray launcher")

    p_load = launcher.add_parser("load", help="Loads scripts")
    p_load.add_argument(
        "loading_scripts", nargs="*", metavar="script_path", type=str, help="Scripts to be loaded"
    )

    p_restart = launcher.add_parser("restart", help="Restarts scripts")
    p_restart.add_argument(
        "restarting_scripts",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Scripts to be restarted",
    )

    p_log = launcher.add_parser(
        "log",
        help=('Views scripts\' logs. Use "launcher log tray-launcher"'
            ' to view the log of the tray launcher')
    )
    p_log.add_argument(
        "log_scripts",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Scripts whose log is to be viewed",
    )
    p_log.add_argument("-a", "--all", action="store_true", help="View all logs")

    p_focus = launcher.add_parser("focus", help="Focus scripts")
    p_focus.add_argument(
        "focusing_scripts", nargs="*", metavar="script_stem", type=str, help="Scripts to be focused"
    )

    p_list = launcher.add_parser("list", help="Lists scripts")
    p_list.add_argument("-r", "--running", action="store_true", help="View all running scripts")
    p_list.add_argument("-a", "--all", action="store_true", help="View all scripts")

    return parser


def main():
    args = get_parser().parse_args()

    if args.launcher == "start":
        print("Starting {}.".format(args.starting_scripts))
        tray_launcher_client.TrayLauncherClient("start", args.starting_scripts).attempt_connect()

    elif args.launcher == "terminate":
        print("Terminating {}.".format(args.terminating_scripts))
        tray_launcher_client.TrayLauncherClient(
            "terminate", args.terminating_scripts
        ).attempt_connect()

    elif args.launcher == "restart":
        print("Restarting {}.".format(args.restarting_scripts))
        tray_launcher_client.TrayLauncherClient(
            "restart", args.restarting_scripts
        ).attempt_connect()

    elif args.launcher == "list":
        if args.running is True:
            print("Currently running scripts: ")
            tray_launcher_client.TrayLauncherClient("list_current", []).attempt_connect()
        elif args.all is True:
            print("All available scripts: ")
            tray_launcher_client.TrayLauncherClient("list", []).attempt_connect()
        else:
            print(
                ("tray_launcher list: error: at least one of the following"
                " arguments are required: -a/--all, -r/--running")
            )

    elif args.launcher == "log":
        if args.all is True:
            print("Showing all logs.")
            tray_launcher_client.TrayLauncherClient("all_logs", []).attempt_connect()
        else:
            print("Showing log of {}.".format(args.log_scripts))
            tray_launcher_client.TrayLauncherClient("log", args.log_scripts).attempt_connect()

    elif args.launcher == "load":
        print("Loading {}.".format(args.loading_scripts))
        tray_launcher_client.TrayLauncherClient("load", args.loading_scripts).attempt_connect()

    elif args.launcher == "focus":
        print("Bringing {} to the foreground.".format(args.focusing_scripts))
        tray_launcher_client.TrayLauncherClient("focus", args.focusing_scripts).attempt_connect()

    elif args.launcher == "run":
        print("Running tray launcher.")
        gui.run_pythonw()

    elif args.launcher == "quit":
        print("Quitting tray launcher.")
        tray_launcher_client.TrayLauncherClient("quit", []).attempt_connect()


if __name__ == "__main__":
    main()
