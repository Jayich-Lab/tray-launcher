import asyncio
import argparse
import os

async def communicate(command, data):
    port = int(os.environ.get("TRAY_LAUNCHER_PORT", 7686))    #Need to use environment variable
    reader, writer = await asyncio.open_connection('127.0.0.1', port)

    writer.write((command + "\n").encode())
    await writer.drain()

    for entry in data:
        writer.write((entry+ "\n").encode())
        await writer.drain()

    # data = await reader.read(100)       #Need to go around this 100
    # print("Received: {}".format(data))

    print("Close the connection")
    writer.close()
    # await writer.wait_closed()



#Automatically takes as raw string, with \\
parser = argparse.ArgumentParser(prog="tray_launcher", description="Manage scripts with the tray launcher.")

parser.add_argument("-s", "--start", nargs="*", metavar="script_stem", type=str, help="Start new script(s).")   #Be able to start multiple scripts in one command line. Exhibit same behavior as if "View in Directory" so can add new scripts to the "scripts"

parser.add_argument("-t", "--terminate", nargs="*", metavar="script_stem", type=str, help="Terminate the script specified.")

parser.add_argument("-l", "--list", action="store_true", help="List all loaded scripts.")   #Should supply an option to only view "currently running"

parser.add_argument("--load", nargs="*", metavar="script_path", type=str, help="Load some scripts.")

parser.add_argument("-r", "--restart", nargs="*", metavar="script_stem", type=str, help="Restart the script specified.")

parser.add_argument("--log", nargs="*", metavar="script_stem", type=str, help="View log of the specified script.")      # This specified script has to be running. If no additional argument is given, do "View All". If parser.log=="tray_launcher", show self logs.

parser.add_argument("-f", "--front", nargs="*", metavar="script_stem", type=str, help="Bring the specified script to the foreground.")

parser.add_argument("-q", "--quit", action="store_true", help="Quit the tray launcher.")


args = parser.parse_args()

if args.start != None:
    print("Starting {}.".format(args.start))
    asyncio.run(communicate((args.start)))

elif args.terminate != None:
    print("Terminating {}.".format(args.terminate))
    asyncio.run(communicate("terminate", args.terminate))

elif args.list == True:
    print("Scripts below: ")
    asyncio.run(communicate("list", []))

elif args.load != None:
    print("Loading {}.".format(args.load))
    asyncio.run(communicate("load", args.load))

elif args.restart != None:
    print("Restarting {}.".format(args.restart))
    asyncio.run(communicate("restart", args.restart))

elif args.log != None:
    print("Showing log of {}.".format(args.log))
    asyncio.run(communicate("log", args.log))

elif args.front != None:
    print("Bringing {} to the foreground.".format(args.front))
    asyncio.run(communicate("front", args.front))

elif args.quit == True:
    print("Quiting tray launcher.")
    asyncio.run(communicate("quit", []))