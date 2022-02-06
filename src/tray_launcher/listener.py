import asyncio
import os

async def handle_echo(reader, writer):
    data = []   #a list of RAW strings, with \\
    while True:
        chunk = await reader.readline()
        if(chunk == b''):      #Assuming an empty byte denotes end of all writings
            break
        data.append(chunk.decode()[:-1])     #To get ride of the "\n"

    # Debugging
    addr = writer.get_extra_info('peername')
    print("Received {} from {}".format(data, addr))

    if(data[0] == "start"):
        return
    elif(data[0] == "terminate"):
        return
    elif(data[0] == "list"):
        return
    elif(data[0] == "load"):
        return
    elif(data[0] == "restart"):
        return
    elif(data[0] == "log"):
        return
    elif(data[0] == "front"):
        return
    elif(data[0] == "quit"):
        return











    # print("Send: {}".format(data))
    # writer.write(data)
    # await writer.drain()

    print("Close the connection \n")
    writer.close()

async def main():
    port = int(os.environ.get("TRAY_LAUNCHER_PORT", 7686))

    server = await asyncio.start_server(handle_echo, '127.0.0.1', port)

    addrs = str(server.sockets[0].getsockname()[1])     #Just to get the port number
    # addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print("Serving on {}".format(addrs))

    async with server:
        await server.serve_forever()

asyncio.run(main())


