import argparse

from tray_launcher import cli, tray_launcher_client


def get_parser():
    parser = argparse.ArgumentParser(
        prog="tray_launcher", description="Manage scripts with the tray launcher"
    )

    launcher = parser.add_subparsers(dest="launcher")
    launcher.required = True

    p_start = launcher.add_parser("start", help="Starts scripts")
    p_start.add_argument(
        "scripts", type=str, nargs="*", metavar="script_stem", help="Scripts to be started"
    )

    launcher.add_parser("quit", help="Quits the tray launcher")

    p_terminate = launcher.add_parser("terminate", help="Terminates scripts")
    p_terminate.add_argument(
        "scripts",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Scripts to be terminated",
    )

    launcher.add_parser("run", help="Runs the tray launcher")

    p_load = launcher.add_parser("load", help="Loads scripts")
    p_load.add_argument(
        "scripts", nargs="*", metavar="script_path", type=str, help="Scripts to be loaded"
    )

    p_restart = launcher.add_parser("restart", help="Restarts scripts")
    p_restart.add_argument(
        "scripts",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Scripts to be restarted",
    )

    p_log = launcher.add_parser(
        "log",
        help=("Views scripts' logs."),
    )
    p_log.add_argument(
        "scripts",
        nargs="*",
        metavar="script_stem",
        type=str,
        help="Scripts whose log is to be viewed",
    )
    p_log.add_argument("-a", "--all", action="store_true", help="View all logs")

    p_focus = launcher.add_parser("focus", help="Focus scripts")
    p_focus.add_argument(
        "scripts", nargs="*", metavar="script_stem", type=str, help="Scripts to be focused"
    )

    p_list = launcher.add_parser("list", help="Lists scripts")
    p_list.add_argument("-r", "--running", action="store_true", help="View all running scripts")
    p_list.add_argument("-a", "--all", action="store_true", help="View all scripts")

    return parser


def get_print_pre_command(launcher, scripts):
    if launcher == "start":
        print_pre_command = "Starting {}.".format(scripts)
    elif launcher == "terminate":
        print_pre_command = "Terminating {}.".format(scripts)
    elif launcher == "restart":
        print_pre_command = "Restarting {}.".format(scripts)
    elif launcher == "load":
        print_pre_command = "Loading {}.".format(scripts)
    elif launcher == "focus":
        print_pre_command = "Bringing {} to the top.".format(scripts)
    return print_pre_command


def dispatch_command(args):
    if args.launcher == "run":
        cli.run_pythonw()
        return

    print_pre_command = ""
    if args.launcher in ["start", "terminate", "restart", "load", "focus"]:
        print_pre_command = get_print_pre_command(args.launcher, args.scripts)
        commands = (args.launcher, args.scripts)
    elif args.launcher == "quit":
        print_pre_command = "Quitting tray launcher."
        commands = ("quit", [])
    elif args.launcher == "log":
        if args.all:
            print_pre_command = "Showing all logs."
            commands = ("all_logs", [])
        else:
            print_pre_command = "Showing logs for {}.".format(args.scripts)
            commands = ("log", args.scripts)
    elif args.launcher == "list":
        if args.running:
            print_pre_command = "Running scripts: "
            commands = ("list_current", [])
        elif args.all:
            print_pre_command = "All available scripts: "
            commands = ("list", [])
        else:
            print(
                (
                    "tray_launcher list: error: at least one of the following"
                    " arguments are required: -a/--all, -r/--running"
                )
            )
            return
    else:
        print("tray_launcher: error: {} is an unrecognized command".format(args.launcher))
        return

    print(print_pre_command)
    tray_launcher_client.TrayLauncherClient(*commands).attempt_connect()


def main():
    args = get_parser().parse_args()
    dispatch_command(args)


if __name__ == "__main__":
    main()
