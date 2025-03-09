import disnake
from disnake.ext import commands
import json
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WARNINGS_FILE = BASE_DIR / "warnings.json"

def load_warnings():
    if not WARNINGS_FILE.exists():
        return {}
    with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_warnings(warnings):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=4)

warnings = load_warnings()

def parse_time(time_str):
    if not time_str:
        return None
    time_str = time_str.lower()
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if time_str[-1] not in multipliers:
        return None
    try:
        value = int(time_str[:-1])
        unit = time_str[-1]
        return value * multipliers[unit]
    except ValueError:
        return None

async def execute_command(command, message):
    guild = message.guild
    author = message.author
    bot_member = guild.me
    args = message.content.split()[1:]
    reason = "No reason provided" if len(args) <= 1 else " ".join(args[1:])

    if not author.guild_permissions.manage_roles and not author.guild_permissions.administrator:
        return disnake.Embed(
            title="Permission Denied",
            description="You need Manage Roles or Administrator permissions to use this command!",
            color=disnake.Color.red()
        )

    if command == "mute":
        if not message.mentions:
            return "Please mention a user to mute!"
        member = message.mentions[0]
        if member == author:
            return "You cannot mute yourself!"
        if member.top_role >= author.top_role:
            return "You cannot mute someone with a higher or equal role!"
        if member.current_timeout:
            return f"{member.mention} is already muted until {member.current_timeout.strftime('%Y-%m-%d %H:%M:%S')}!"
        duration = parse_time(args[1] if len(args) > 1 else None)
        timeout_until = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=duration) if duration else None
        try:
            await member.timeout(until=timeout_until, reason=reason)
            embed = disnake.Embed(
                title="User Muted",
                description=f"{member.mention} has been muted.\n**Reason:** {reason}\n**Action by:** {author.mention}",
                color=disnake.Color.green()
            )
            if duration:
                embed.add_field(name="Duration", value=f"{args[1]} (until {timeout_until.strftime('%Y-%m-%d %H:%M:%S')})", inline=False)
            return embed
        except disnake.errors.Forbidden:
            return disnake.Embed(
                title="Error",
                description="Bot lacks permissions to mute this user! Please ensure I have 'Moderate Members' permission and a higher role.",
                color=disnake.Color.red()
            )

    elif command == "unmute":
        if not message.mentions:
            return "Please mention a user to unmute!"
        member = message.mentions[0]
        if not member.current_timeout:
            return f"{member.mention} is not muted!"
        try:
            await member.timeout(until=None, reason=reason)
            return disnake.Embed(
                title="User Unmuted",
                description=f"{member.mention} has been unmuted.\n**Reason:** {reason}\n**Action by:** {author.mention}",
                color=disnake.Color.green()
            )
        except disnake.errors.Forbidden:
            return disnake.Embed(
                title="Error",
                description="Bot lacks permissions to unmute this user! Please ensure I have 'Moderate Members' permission and a higher role.",
                color=disnake.Color.red()
            )

    elif command == "kick":
        if not message.mentions:
            return "Please mention a user to kick!"
        member = message.mentions[0]
        if member.top_role >= author.top_role:
            return "You cannot kick someone with a higher or equal role!"
        await member.kick(reason=reason)
        return disnake.Embed(
            title="User Kicked",
            description=f"{member.mention} has been kicked.\n**Reason:** {reason}\n**Action by:** {author.mention}",
            color=disnake.Color.orange()
        )

    elif command == "ban":
        if not message.mentions:
            return "Please mention a user to ban!"
        member = message.mentions[0]
        if member.top_role >= author.top_role:
            return "You cannot ban someone with a higher or equal role!"
        await member.ban(reason=reason)
        return disnake.Embed(
            title="User Banned",
            description=f"{member.mention} has been banned.\n**Reason:** {reason}\n**Action by:** {author.mention}",
            color=disnake.Color.red()
        )

    elif command == "warn":
        if not message.mentions:
            return "Please mention a user to warn!"
        member = message.mentions[0]
        if member == author:
            return "You cannot warn yourself!"

        warnings[member.id] = warnings.get(member.id, 0) + 1
        warn_count = warnings[member.id]
        save_warnings(warnings)

        embed = disnake.Embed(
            title="User Warned",
            description=f"{member.mention} has been warned.\n**Reason:** {reason}\n**Warnings:** {warn_count}/4\n**Action by:** {author.mention}",
            color=disnake.Color.yellow()
        )
        await member.send(embed=embed)

        if warn_count >= 4:
            if member.top_role >= bot_member.top_role:
                embed.add_field(
                    name="Auto-Mute Failed",
                    value="Cannot mute this user due to higher or equal role! Warnings reset.",
                    inline=False
                )
                warnings[member.id] = 0
                save_warnings(warnings)
            else:
                try:
                    timeout_until = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=25)
                    await member.timeout(until=timeout_until, reason="Reached 4 warnings")
                    embed.add_field(
                        name="User Muted",
                        value=f"{member.mention} has been muted for reaching 4 warnings.\n**Duration:** 25m (until {timeout_until.strftime('%Y-%m-%d %H:%M:%S')})",
                        inline=False
                    )
                    warnings[member.id] = 0
                    save_warnings(warnings)
                except disnake.errors.Forbidden:
                    embed.add_field(
                        name="Auto-Mute Failed",
                        value="Bot lacks permissions to mute this user! Warnings reset.",
                        inline=False
                    )
                    warnings[member.id] = 0
                    save_warnings(warnings)
        return embed

    elif command == "clear":
        try:
            amount = int(args[0]) if args else 10
            if amount < 1 or amount > 100:
                return "Please specify a number between 1 and 100!"
            deleted = await message.channel.purge(limit=amount + 1)
            return disnake.Embed(
                title="Messages Cleared",
                description=f"Cleared {len(deleted) - 1} messages.\n**Action by:** {author.mention}",
                color=disnake.Color.blue()
            )
        except ValueError:
            return "Please provide a valid number of messages to clear!"

    elif command == "userinfo":
        member = message.mentions[0] if message.mentions else author
        embed = disnake.Embed(
            title=f"User Info: {member}",
            color=disnake.Color.purple()
        )
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Roles", value=", ".join([r.name for r in member.roles[1:]]), inline=False)
        warn_count = warnings.get(member.id, 0)
        embed.add_field(name="Warnings", value=f"{warn_count}/4", inline=False)
        if member.current_timeout:
            embed.add_field(name="Muted Until", value=member.current_timeout.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        return embed

    return None