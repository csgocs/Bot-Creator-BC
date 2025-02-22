import disnake

async def execute_command(command, message=None):
    if not message:
        return "Error: No message context provided."
    cmd = command.lower()
    parts = message.content.split()
    if not message.author.guild_permissions.administrator:
        embed = disnake.Embed(
            title="Permission Denied",
            description="You need administrator permissions to use this command!",
            color=disnake.Color.red()
        )
        return embed
    if cmd == "kick" and len(parts) > 1:
        try:
            member = message.mentions[0]
            reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"
            await member.kick(reason=reason)
            embed = disnake.Embed(
                title="User Kicked",
                description=f"**{member.name}#{member.discriminator}** has been kicked.",
                color=disnake.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Action by {message.author.name}")
            return embed
        except Exception as e:
            embed = disnake.Embed(
                title="Error",
                description=f"Failed to kick user: {str(e)}",
                color=disnake.Color.red()
            )
            return embed
    if cmd == "ban" and len(parts) > 1:
        try:
            member = message.mentions[0]
            reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"
            await member.ban(reason=reason)
            embed = disnake.Embed(
                title="User Banned",
                description=f"**{member.name}#{member.discriminator}** has been banned.",
                color=disnake.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Action by {message.author.name}")
            return embed
        except Exception as e:
            embed = disnake.Embed(
                title="Error",
                description=f"Failed to ban user: {str(e)}",
                color=disnake.Color.red()
            )
            return embed
    if cmd == "mute" and len(parts) > 1:
        try:
            member = message.mentions[0]
            reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"
            muted_role = disnake.utils.get(message.guild.roles, name="Muted")
            if not muted_role:
                embed = disnake.Embed(
                    title="Error",
                    description="Muted role not found! Please create a 'Muted' role.",
                    color=disnake.Color.red()
                )
                return embed
            await member.add_roles(muted_role, reason=reason)
            embed = disnake.Embed(
                title="User Muted",
                description=f"**{member.name}#{member.discriminator}** has been muted.",
                color=disnake.Color.blue()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Action by {message.author.name}")
            return embed
        except Exception as e:
            embed = disnake.Embed(
                title="Error",
                description=f"Failed to mute user: {str(e)}",
                color=disnake.Color.red()
            )
            return embed
    if cmd == "unmute" and len(parts) > 1:
        try:
            member = message.mentions[0]
            reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"
            muted_role = disnake.utils.get(message.guild.roles, name="Muted")
            if not muted_role:
                embed = disnake.Embed(
                    title="Error",
                    description="Muted role not found! Please create a 'Muted' role.",
                    color=disnake.Color.red()
                )
                return embed
            await member.remove_roles(muted_role, reason=reason)
            embed = disnake.Embed(
                title="User Unmuted",
                description=f"**{member.name}#{member.discriminator}** has been unmuted.",
                color=disnake.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Action by {message.author.name}")
            return embed
        except Exception as e:
            embed = disnake.Embed(
                title="Error",
                description=f"Failed to unmute user: {str(e)}",
                color=disnake.Color.red()
            )
            return embed
    return None