import asyncio

async def waiter(event):
    print('waiting for it ...')
    while True:
        await event.wait()
        event.clear()
        print('... got it!')

async def main():
    # Create an Event object.
    event = asyncio.Event()

    # Spawn a Task to wait until 'event' is set.
    waiter_task = asyncio.create_task(waiter(event))

    # Sleep for 1 second and set the event.
    while True:
        await asyncio.sleep(1)
        event.set()

    # Wait until the waiter task is finished.
    await waiter_task

asyncio.run(main())