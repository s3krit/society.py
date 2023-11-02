import time
import niobot
import logging
import society
import asyncio
import os
from dotenv import load_dotenv
from niobot import Context

load_dotenv()

room = os.getenv("MATRIX_ROOM")
matrix_access_token = os.getenv("MATRIX_TOKEN")
rpc_url = os.getenv("RPC_URL")
db_path = os.getenv("DB_PATH")
prefix = os.getenv("PREFIX")
loglevel = os.getenv("LOGLEVEL") or "INFO"
logging.getLogger()
logging.basicConfig(level=loglevel)
logging.info("Logging level: {}".format(loglevel))
society.init(rpc_url, db_path)

bot = niobot.NioBot(
    homeserver = "https://matrix.org",
    user_id = "@societybot:matrix.org",
    command_prefix = prefix,
    case_insensitive = False,
    owner_id = "@s3krit:fairydust.space"
)

# Formats a list as a markdown bulleted list
def format_list(list):
    response = ""
    for item in list:
        response += "* {}\n".format(item)
    return response

async def period_message():
    last_blocks_left = 0
    first_run = True
    while True:
        blocks_left = society.get_blocks_until_next_period()
        logging.info("Blocks left until next period: {}".format(blocks_left))
        if blocks_left > last_blocks_left and not first_run:
            defender = society.get_defender()
            candidates = society.get_candidates()
            head = society.get_head_address()

            message = """\
A new period has started. Blocks until next period: {}

The current defender is {}.
""".format(blocks_left, defender)
            if len(candidates) > 0:
                message += """
The current candidates are:\n{}
                
The current head is: {}.""".format(format_list(candidates), head)
            else:
                message += """
There are no candidates for this period."""
            logging.info(message)
            await bot.send_message(room, message)

        last_blocks_left = blocks_left
        first_run = False
        await asyncio.sleep(60)

async def get_info(address):
    info = society.get_member_info(address)
    if info:
        response = ""
        for key in info:
            response += "* **{}**: {}\n".format(key.capitalize(), info[key])
        return response
    else:
        None

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

@bot.command()
async def ping(ctx: Context):
    """Shows the roundtrip latency"""
    roundtrip = (time.time() * 1000 - ctx.event.server_timestamp)
    await ctx.respond("Pong! Took {:,.2f}ms".format(roundtrip))

@bot.command()
async def defender(ctx: Context):
    """Shows the current defender"""
    defender = society.get_defender()
    if defender:
        await ctx.respond("The current defender is {}".format(defender))
    else:
        await ctx.respond("There is no defender")

@bot.command()
async def info(ctx: Context, address: str):
    """Shows info about a given Kusama address."""
    if len(ctx.args) < 1:
        await ctx.respond("Usage: `!info <address>`")
        return
    address = ctx.args[0]
    info = await get_info(address)
    if info:
        await ctx.respond(info)
    else:
        await ctx.respond("No info available for that address")

@bot.command()
async def candidates(ctx: Context):
    """Shows the current candidates"""
    candidates = society.get_candidates_addresses()
    if len(candidates) > 0:
        await ctx.respond("The current candidates are:\n{}".format(format_list(candidates)))
    else:
        await ctx.respond("There are no candidates")

@bot.command()
async def head(ctx: Context):
    """Shows the current head"""
    head = society.get_head_address()
    if head:
        await ctx.respond("The current head is `{}`".format(head))
    else:
        await ctx.respond("There is no head, something must have gone horribly wrong")
    

@bot.command()
async def set_address(ctx: Context, address: str):
    """Sets a Kusama address for your matrix handle."""
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
    """Unsets a Kusama address for your matrix handle"""
    if society.unset_matrix_handle():
        await ctx.respond("Unset address for {}".format(ctx.message.sender))
    else:
        await ctx.respond("Failed to unset address for {}".format(ctx.message.sender))

@bot.command()
async def me(ctx: Context):
    """Shows info about you."""
    address = society.get_address_for_matrix_handle(ctx.message.sender)
    if address:
        info = await get_info(address)
        await ctx.respond(info)
    else:
        await ctx.respond("You have not set your address yet. To do so, use `!set_address <address>`. Note that the !me command does not currently support addresses with an on-chain identity set.")

bot.run(access_token=matrix_access_token)
