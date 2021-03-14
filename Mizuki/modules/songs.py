import time
import os
import json
from telethon.tl.types import DocumentAttributeAudio
from youtube_dl import YoutubeDL

from youtube_dl.utils import (
    DownloadError,
    ContentTooShortError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from Mizuki import tbot
from telethon import types
from telethon.tl import functions
from Mizuki.events import register
from youtubesearchpython import SearchVideos
from pymongo import MongoClient
from Mizuki import MONGO_DB_URI

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["missjuliarobot"]
approved_users = db.approve


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


MIZUKISONG = "@MizukiSongs"


@register(pattern="^/song (.*)")
async def download_song(v_url):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if v_url.is_group:
        if await is_register_admin(v_url.input_chat, v_url.message.sender_id):
            pass
        elif v_url.chat_id == iid and v_url.sender_id == userss:
            pass
        else:
            return
    url = v_url.pattern_match.group(1)
    rkp = await v_url.reply("**Processing**")
    if not url:
        await rkp.edit("**No!**\nUsage`/song <song name>`")
    search = SearchVideos(url, offset=1, mode="json", max_results=1)
    test = search.result()
    p = json.loads(test)
    q = p.get("search_result")
    try:
        url = q[0]["link"]
    except BaseException:
        return await rkp.edit("`Failed to find that song`")
    type = "audio"
    await rkp.edit("**Preparing to download by @Infinity_BOTs**")
    if type == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        video = False
        song = True
    try:
        await rkp.edit("**Searching song, please wait 😁**")
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except DownloadError as DE:
        await rkp.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await rkp.edit("`The download content was too short.`")
        return
    except GeoRestrictedError:
        await rkp.edit(
            "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
        )
        return
    except MaxDownloadsReached:
        await rkp.edit("`Max-downloads limit has been reached.`")
        return
    except PostProcessingError:
        await rkp.edit("`There was an error during post processing.`")
        return
    except UnavailableVideoError:
        await rkp.edit("`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await rkp.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await rkp.edit("`There was an error during info extraction.`")
        return
    except Exception as e:
        await rkp.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()
    if song:
        await rkp.edit(f"**Sending the song 🤗**")

        y = await v_url.client.send_file(
            v_url.chat_id,
            f"{rip_data['id']}.mp3",
            supports_streaming=False,
            force_document=False,
            allow_cache=False,
            attributes=[
                DocumentAttributeAudio(
                    duration=int(rip_data["duration"]),
                    title=str(rip_data["title"]),
                    performer=str(rip_data["uploader"]),
                )
            ],
        )
        await y.forward_to(MIZUKISONG)
        os.system("rm -rf *.mp3")
        os.system("rm -rf *.webp")


__help__ = """
 • `/song <song name>`*:* uploads the song in the best quality available.
 • `/saavn <song name>`*:* uploads the song from Jio Saavn in best quality.
 • `/lyrics <song name>`*:* provides the lyrics of the song you want.
"""

__mod_name__ = "Songs 🎵"
