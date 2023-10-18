import time
import niobot
import logging
import society
import asyncio
import os
from dotenv import load_dotenv
from niobot import Context

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

room = os.getenv("MATRIX_ROOM")
matrix_access_token = os.getenv("MATRIX_TOKEN")
rpc_url = os.getenv("RPC_URL")
db_path = os.getenv("DB_PATH")

society.init(rpc_url, db_path)

bot = niobot.NioBot(
    homeserver = "https://matrix.org",
    user_id = "@societybot:matrix.org",
    command_prefix = "!",
    case_insensitive = False,
    owner_id = "@s3krit:fairydust.space"
)

async def periodic_reconnect():
    while True:
        # Reconnect every 10 minutes
        await asyncio.sleep(600)
        society.init(rpc_url, db_path)

async def period_message():
    last_blocks_left = 0
    while True:
        blocks_left = society.get_blocks_until_next_period()
        print("Blocks left until next period: {}".format(blocks_left))
        if blocks_left > last_blocks_left:
            defender = society.get_defender()
            candidates = society.get_candidates()
            head = society.get_head_address()

            message = """\
A new period has started. Blocks until next period: {}

The current defender is `{}`.
""".format(blocks_left, defender)
            if len(candidates) > 0:
                message += """
The current candidates are: `{}`
                
The new head is `{}`.""".format(candidates, head)
            else:
                message += """
There are no candidates for this period."""
            print(message)
            await bot.send_message(room, message)

        last_blocks_left = blocks_left
        await asyncio.sleep(60)

@bot.on_event("command_error")
async def on_command_error(ctx: Context, error: Exception):
    if isinstance(error, niobot.CommandArgumentsError):
        await ctx.respond("Invalid arguments: " + str(error))
    elif isinstance(error, niobot.CommandDisabledError):
        await ctx.respond("Command disabled: " + str(error))
    else:
        error = getattr(error, 'exception', error)
        await ctx.respond("Error: " + str(error))
        bot.log.error('command error in %s: %r', ctx.command.name, error, exc_info=error)

@bot.on_event("ready")
async def on_ready(_: niobot.SyncResponse):
    asyncio.create_task(period_message())
    asyncio.create_task(periodic_reconnect())

@bot.command()
async def ping(ctx: Context):
    roundtrip = (time.time() * 1000 - ctx.event.server_timestamp)
    await ctx.respond("Pong! Took {:,.2f}ms".format(roundtrip))

@bot.command()
async def defender(ctx: Context):
    defender = society.get_defender()
    if defender:
        await ctx.respond("The current defender is `{}`".format(defender))
    else:
        await ctx.respond("There is no defender")

@bot.command()
async def info(ctx: Context, address: str):
    if len(ctx.args) < 1:
        await ctx.respond("Usage: `!info <address>`")
        return
    address = ctx.args[0]
    info = society.get_member_info(address)
    if info:
        response = ""
        for key in info:
            response += "* **{}**: {}\n".format(key.capitalize(), info[key])
        await ctx.respond(response)
    else:
        await ctx.respond("No info available for that address")

@bot.command()
async def candidates(ctx: Context):
    candidates = society.get_candidates_addresses()
    if len(candidates) > 0:
        await ctx.respond("The current candidates are `{}`".format(candidates))
    else:
        await ctx.respond("There are no candidates")

@bot.command()
async def head(ctx: Context):
    head = society.get_head_address()
    if head:
        await ctx.respond("The current head is `{}`".format(head))
    else:
        await ctx.respond("There is no head, something must have gone horribly wrong")
    

@bot.command()
async def set_address(ctx: Context, address: str):
    if len(ctx.args) < 1:
        await ctx.respond("Usage: `!set_address <address>`")
        return
    address = ctx.args[0]
    matrix_handle = ctx.message.sender
    if society.set_matrix_handle(address, matrix_handle):
        await ctx.respond("Set matrix handle {} for address `{}`".format(matrix_handle, address))
    else:
        await ctx.respond("Failed to set matrix handle {} for address `{}`".format(matrix_handle, address))

@bot.command()
async def unset_address(ctx: Context):
    if society.unset_matrix_handle():
        await ctx.respond("Unset address for {}".format(ctx.message.sender))
    else:
        await ctx.respond("Failed to unset address for {}".format(ctx.message.sender))

@bot.command()
async def reconnect(ctx: Context):
    society.init(rpc_url, db_path)
    await ctx.respond("Reconnected to RPC")

@bot.command()
async def usage(ctx: Context):
    await ctx.respond("Usage: `!ping`, `!defender`, `!info <address>`, `!candidates`, `!head`, `!set_address <address>`, `!unset_address`, `!reconnect`")

bot.run(access_token=matrix_access_token)