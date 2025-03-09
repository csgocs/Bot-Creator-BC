import disnake
from disnake.ext import commands
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
HELP_FILE = BASE_DIR / "help.json"

def create_default_help():
    default_help = {
        "color": 7506394,
        "title": "Hello!",
        "description": "Go to the path where you saved BC, find help.json, and edit it as you like!",
        "image": {"url": ""},
        "thumbnail": {"url": ""},
        "author": {"name": "test", "icon_url": ""},
        "footer": {"text": "Footer Text", "icon_url": ""},
        "fields": [
            {"name": "test", "value": "test_1"},
            {"name": "test", "value": "test_2"}
        ]
    }
    with open(HELP_FILE, "w", encoding="utf-8") as f:
        json.dump(default_help, f, indent=4)
    return default_help

async def execute_command(command, message):
    if command == "help":
        if not HELP_FILE.exists():
            help_data = create_default_help()
        else:
            with open(HELP_FILE, "r", encoding="utf-8") as f:
                help_data = json.load(f)

        embed = disnake.Embed(
            title=help_data.get("title", "Help"),
            description=help_data.get("description", "No description provided"),
            color=help_data.get("color", disnake.Color.blue())
        )

        if help_data.get("image", {}).get("url"):
            embed.set_image(url=help_data["image"]["url"])
        if help_data.get("thumbnail", {}).get("url"):
            embed.set_thumbnail(url=help_data["thumbnail"]["url"])
        if help_data.get("author", {}).get("name"):
            embed.set_author(
                name=help_data["author"]["name"],
                icon_url=help_data["author"].get("icon_url", "")
            )
        if help_data.get("footer", {}).get("text"):
            embed.set_footer(
                text=help_data["footer"]["text"],
                icon_url=help_data["footer"].get("icon_url", "")
            )

        for field in help_data.get("fields", []):
            embed.add_field(
                name=field.get("name", "No name"),
                value=field.get("value", "No value"),
                inline=False
            )

        return embed
    
    return None