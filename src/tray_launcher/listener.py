import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = list(data)

    info = []
    for i in len(message):
        info.append(message[i].decode())
    addr = writer.get_extra_info('peername')

    print("Received {} from {}".format(message, addr))

    # print("Send: {}".format(data))
    # writer.write(data)
    # await writer.drain()

    print("Close the connection")
    writer.close()

# async def handle_echo(reader, writer):
#     data = await reader.read()

#     message = data.decode()
#     print("Received {}".format(message))

#     print("Send: {}".format(data))
#     writer.write(data)
#     await writer.drain()

#     print("Close the connection")
#     writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 0)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print("Serving on {}".format(addrs))

    async with server:
        await server.serve_forever()

asyncio.run(main())