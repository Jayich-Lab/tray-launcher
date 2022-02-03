import asyncio

async def echo_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print("Send: {}".format(message))
    writer.write(message.encode())

    data = await reader.read(100)
    print("Received: {}".format(data.decode()))

    print("Close the connection")
    writer.close()
    # await writer.wait_closed()

asyncio.run(echo_client("Hello World"))