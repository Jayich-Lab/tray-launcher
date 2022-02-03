import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print("Received {} from {}".format(message, addr))

    print("Send: {}".format(data))
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()
    # await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 0)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print("Serving on {}".format(addrs))

    async with server:
        await server.serve_forever()

asyncio.run(main())