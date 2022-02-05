import asyncio
import argparse

# async def communicate(command, args):
#     port = 59049    #Read from a shared file, created everytime the tray_launcher is launched. Or, should we update it every say 5 hours?

#     reader, writer = await asyncio.open_connection('127.0.0.1', port)

#     writer.write("Message".encode())   #Let's see how it's like without .encode()

#     data = await reader.read()
#     print(data.decode())

#     writer.close()
#     #await writer.wait_closed()

async def communicate(data):

    reader, writer = await asyncio.open_connection('127.0.0.1', 54749)
    print("Send: {}".format(bytes(data)))
    writer.write(data)

    # data = await reader.read(100)       #Need to go around this 100
    # print("Received: {}".format(data))

    print("Close the connection")
    writer.close()
    # await writer.wait_closed()




parser = argparse.ArgumentParser(prog="tray_launcher", description="Manage scripts with the tray launcher.")

parser.add_argument("-s", "--start", nargs="*", metavar="script_stem", type=str, help="Start new script(s).")

parser.add_argument("-t", "--terminate", nargs=1, metavar="script_stem", type=str, help="Terminate the script specified.")

parser.add_argument("-l", "--list", action="store_true", help="List all loaded scripts.")

parser.add_argument("--load", nargs="*", metavar="script_path", type=str, help="Load some scripts.")

parser.add_argument("-r", "--restart", nargs=1, metavar="script_stem", type=str, help="Restart the script specified.")

parser.add_argument("--log", nargs=1, metavar="script_stem", type=str, help="View log of the specified script.")      # This specified script has to be running. If it is not running, show the same behavior as "--logs". If parser.log=="tray_launcher", show self logs.

parser.add_argument("--logs", action="store_true", help="View all logs.")

parser.add_argument("-f", "--front", nargs=1, metavar="script_stem", type=str, help="Bring the specified script to the foreground.")

parser.add_argument("-q", "--quit", action="store_true", help="Quit the tray launcher.")


args = parser.parse_args()

if args.start != None:
    info = [("start").encode()]
    for i in args.start:
        print("Starting {}.".format(i))
        m = i.encode()
        print(m)
        info.append(m)
    print(info)
    asyncio.run(communicate((info)))


elif args.terminate != None:
    print("Terminating {}.".format(args.terminate))
    asyncio.run(communicate("terminate", args.terminate))
elif args.list == True:
    print("Scripts below: ")
    asyncio.run(communicate("list", None))
elif args.load != None:
    print("Loading {}.".format(args.load))
    asyncio.run(communicate("load", args.load))
elif args.restart != None:
    print("Restarting {}.".format(args.restart))
    asyncio.run(communicate("restart", args.restart))
elif args.log != None:
    print("Showing log of {}.".format(args.log))
    asyncio.run(communicate("log", args.log))
elif args.logs == True:
    print("Opening up all logs.")
    asyncio.run(communicate("logs", None))
elif args.front != None:
    print("Bringing {} to the foreground.".format(args.front))
    asyncio.run(communicate("front", args.front))
elif args.quit == True:
    print("Quiting tray launcher.")
    asyncio.run(communicate("quit", None))
