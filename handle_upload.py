import os
import aiohttp
from urllib.parse import urlparse
from poi.job import job
from society import is_valid_address

class HandleUpload:
    def __init__(self, client, room, event):
        self.client = client
        self.room = room
        self.event = event

    def is_caller_whitelisted(self):
        whitelist = ["@laurogripa:matrix.org", "@s3krit:fairydust.space", "@rtti-5220:matrix.org"]
        return self.event.sender in whitelist

    async def handle(self, command, soc):
        if not is_valid_command(command, self.event):
            return

        if not self.is_caller_whitelisted():
            await self.respond("Unauthorized")
            return

        args = split_into_args(command)
        if len(args) < 1 or len(args) > 2:
            return

        original_event = await self.fetch_original_event()
        if not is_image(original_event):
            await self.respond("You are not replying to an image. Usage: `!upload <address> [force]` replying to an image")
            return

        address = args[0]
        if not is_valid_address(address):
            await self.respond("The address provided is not valid")
            return

        if not soc.is_member(address):
            await self.respond("The address provided is not a member")
            return

        image_url = extract_image_url(original_event)
        (success, save_path) = await self.download_image(image_url, 'poi/temp')

        if not success:
            await self.respond(f"Failed to download image")
            return False

        force = len(args) > 1 and args[1] == 'force'
        upload, message = job(save_path, address, force)
        if upload:
            await self.respond("File uploaded to IPFS. See gallery here: https://ksmsociety.io/explore/poi/gallery")
        else:
            await self.respond("Upload failed: {}".format(message))

    async def respond(self, message):
        await self.client.room_send(
            room_id=self.room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message,
                "m.relates_to": {
                    "m.in_reply_to": {
                        "event_id": self.event.event_id
                    }
                }
            }
        )

    async def fetch_original_event(self):
        original_event_id = extract_original_event_id(self.event)
        if original_event_id:
            original_event = await self.fetch_event(original_event_id)
            return original_event

    async def fetch_event(self, original_event_id):
        response = await self.client.room_get_event(self.room.room_id, original_event_id)
        return response.event if response else None

    async def download_image(self, url, save_dir):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        image_name = os.path.basename(urlparse(url).path)
        save_path = os.path.join(save_dir, image_name)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()

                    with open(save_path, 'wb') as file:
                        file.write(image_data)
                    return True, save_path

        return False, None

# Helpers

def is_valid_command(command, event):
    reply = event.formatted_body

    if not reply:
        return event.body.startswith(command)
    else:
        body_without_reply = event.body.split('\n\n', 1)[1] if '\n\n' in event.body else ''
        return body_without_reply.startswith(command)

def is_image(original_event):
    if original_event:
        return original_event.source.get('content', {}).get('msgtype') == "m.image"

def extract_image_url(event):
    mxc_url = event.source.get('content', {}).get('url', '')
    server_name, media_id = mxc_url[len("mxc://"):].split("/", 1)
    server_url = "https://matrix-client.matrix.org"
    return f"{server_url}/_matrix/media/r0/download/{server_name}/{media_id}"

def extract_original_event_id(event):
    if event:
        return (event.source.get('content', {})
                        .get('m.relates_to', {})
                        .get('m.in_reply_to', {})
                        .get('event_id'))

def split_into_args(string):
    args = string.split()
    return args[1:]
