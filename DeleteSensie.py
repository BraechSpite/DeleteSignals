from telethon import TelegramClient, events
import nest_asyncio
import asyncio
from aiohttp import web
import os

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Use your actual API credentials (stored as environment variables for security)
api_id = 22557209  # Your API ID
api_hash = '2c2cc680074bcfa5e77f2773ff6e565b'  # Your API Hash
phone_number = '+919956915970'  # Your phone number

# Initialize the client using the saved session file
client = TelegramClient('userbot', api_id, api_hash)

# Store connected channels
connected_channels = []

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "Welcome to the Message Delete Bot!\n\n"
        "Here are the features:\n"
        "1. Connect to a channel using /connect <channel_id>\n"
        "2. Select specific words to delete using /delete <start_message_id> <end_message_id> <words>\n"
        "3. The bot can read text and emojis.\n"
        "4. After deleting messages, it will notify you that the task is done."
    )

@client.on(events.NewMessage(pattern='/connect'))
async def connect(event):
    if len(event.message.message.split()) < 2:
        await event.respond("Please provide a channel ID. Usage: /connect <channel_id>")
        return

    channel_id = int(event.message.message.split()[1])  # Ensure the ID is an integer
    connected_channels.append(channel_id)
    await event.respond(f"Connected to channel {channel_id}")

@client.on(events.NewMessage(pattern='/delete'))
async def delete(event):
    args = event.message.message.split()

    if len(args) < 4:
        await event.respond("Please provide the start message ID, end message ID, and words to delete. Usage: /delete <start_message_id> <end_message_id> <words>")
        return

    start_message_id = int(args[1])
    end_message_id = int(args[2])
    words_to_delete = args[3:]

    for channel_id in connected_channels:
        try:
            async for message in client.iter_messages(channel_id, min_id=start_message_id, max_id=end_message_id + 1):
                if any(word in message.message for word in words_to_delete):
                    await client.delete_messages(entity=channel_id, message_ids=[message.id])
                    print(f"Deleted message ID {message.id}")
        except Exception as e:
            print(f"Error fetching or deleting messages: {e}")

    await event.respond("Task is done")

# Set up a simple web server to satisfy Render's port requirement
async def handle(request):
    return web.Response(text="Bot is running")

async def main():
    # Start the client without asking for a code, using the saved session
    await client.start(phone=phone_number)

    # Start the web server
    app = web.Application()
    app.router.add_get('/', handle)

    # Get the port from environment variable or use 8080
    port = int(os.environ.get('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print(f"Server started at http://0.0.0.0:{port}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
