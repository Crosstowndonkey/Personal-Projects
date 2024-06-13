import discord
from discord.ext import tasks
import requests
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Get the bot token from an environment variable for security
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CAT_API_URL = '#cat_api_url'

# Initialize the bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
scheduler = AsyncIOScheduler()


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Start the scheduled task
    scheduler.start()
    post_cat_pictures.start()


@tasks.loop(hours=4)  # Change this interval as needed
async def post_cat_pictures():
    # Specify the channel ID where the bot will post cat pictures
    channel_id = #channel id here
    channel = client.get_channel(channel_id)

    if channel is not None:
        cat_picture_url = get_cat_picture_url()
        if cat_picture_url:
            await channel.send(cat_picture_url)
        else:
            await channel.send("Could not retrieve a cat picture at this time.")
    else:
        print(f"Channel with ID {channel_id} not found.")


def get_cat_picture_url():
    response = requests.get(CAT_API_URL)
    if response.status_code == 200:
        data = response.json()
        return data[0]['url'] if data else None
    return None


# Run the bot
if TOKEN:
    client.run(TOKEN)
else:
    print("Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
