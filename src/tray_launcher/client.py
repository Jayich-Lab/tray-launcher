import asyncio
import argparse

parser = argparse.ArgumentParser(prog="tray_launcher", description="Manage scripts with the tray launcher.", add_help=False)

# parser.add_argument("-s", "--start", nargs=1, metavar="script_stem", type=str, help="Start a new script")

# parser.add_argument("terminate", nargs=1, metavar="script_stem", type=str, help="Terminate the script specified.")

# parser.add_argument("restart", nargs=1, metavar="script_stem", type=str, help="Restart the script specified.")

# parser.add_argument("list", help="List all loaded scripts.")

# parser.add_argument("load", nargs="*", metavar="script_path", type=str, help="Load some scripts.")

# parser.add_argument("quit", help="Quit the tray launcher.")

# parser.add_argument("logs", help="View all logs.")

# parser.add_argument("log", nargs=1, metavar="script_stem", type=str, help="View log of the specified script.")     # This specified script has to be running. If parser.log=="tray_launcher", show self logs.

parser.add_argument("-h", "--help", help="Display help messages.")
parser.add_argument("options", nargs="*", type=str)
#Need to write the help myself
args = parser.parse_args()

print(args.multiply)
# async def echo_client(message):
#     reader, writer = await asyncio.open_connection('127.0.0.1', 61982)
#     print("Send: {}".format(message))
#     writer.write(message.encode())

#     data = await reader.read(100)
#     print("Received: {}".format(data.decode()))

#     print("Close the connection")
#     writer.close()
#     # await writer.wait_closed()

# asyncio.run(echo_client("Hello World"))