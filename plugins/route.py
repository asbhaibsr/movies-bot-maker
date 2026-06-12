# ════════════════════════════════════════════════
#   plugins/route.py — aiohttp Web Routes
#   Health check + Telegram file streaming
# ════════════════════════════════════════════════

import math
import logging
import mimetypes

from aiohttp import web
from info import LOG_CHANNEL, IS_STREAM

from AsBhai.server.exceptions import InvalidHash, FIleNotFound

routes = web.RouteTableDef()

# ── Simple cache so ByteStreamer is reused per client ─────────────────────────
_byte_streamers = {}


# ── Health-check / root ───────────────────────────────────────────────────────
@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "running", "server": "AsBhai Bot"})


# ── Web-page for watch/stream (IS_STREAM mode) ───────────────────────────────
@routes.get("/watch/{message_id}/{secure_hash}", allow_head=True)
async def stream_page_handler(request):
    if not IS_STREAM:
        raise web.HTTPServiceUnavailable(text="Streaming is disabled on this instance.")
    try:
        message_id = int(request.match_info["message_id"])
        secure_hash = request.match_info["secure_hash"]
        from AsBhai.util.render_template import render_page
        page = await render_page(message_id, secure_hash)
        return web.Response(text=page, content_type="text/html")
    except InvalidHash:
        raise web.HTTPForbidden(text="Invalid link hash.")
    except FIleNotFound:
        raise web.HTTPNotFound(text="File not found.")
    except Exception as e:
        logging.error(f"stream_page_handler error: {e}", exc_info=True)
        raise web.HTTPInternalServerError(text="Something went wrong.")


# ── Raw file stream / download ────────────────────────────────────────────────
@routes.get("/{message_id}/{file_name}", allow_head=True)
async def stream_handler(request):
    if not IS_STREAM:
        raise web.HTTPServiceUnavailable(text="Streaming is disabled on this instance.")
    try:
        message_id = int(request.match_info["message_id"])
        file_name  = request.match_info["file_name"]
        secure_hash = request.rel_url.query.get("hash", "")
        return await media_streamer(request, message_id, secure_hash, file_name)
    except InvalidHash:
        raise web.HTTPForbidden(text="Invalid link hash.")
    except FIleNotFound:
        raise web.HTTPNotFound(text="File not found.")
    except (ValueError, AttributeError) as e:
        logging.error(f"stream_handler error: {e}", exc_info=True)
        raise web.HTTPInternalServerError(text="Something went wrong.")


async def media_streamer(request, message_id: int, secure_hash: str, file_name: str):
    """Stream a Telegram file with HTTP Range support."""
    from AsBhai.bot import multi_clients, work_loads, AsBhaiBot
    from AsBhai.util.custom_dl import ByteStreamer
    from AsBhai.util.file_properties import get_file_ids

    range_header = request.headers.get("Range", None)

    # Pick the least-loaded client
    if work_loads:
        index  = min(work_loads, key=work_loads.get)
        client = multi_clients.get(index, AsBhaiBot)
    else:
        index  = 0
        client = AsBhaiBot

    # Fetch file metadata from Telegram
    file_id = await get_file_ids(client, int(LOG_CHANNEL), message_id)
    if not file_id:
        raise FIleNotFound

    # Verify the short hash
    if secure_hash and file_id.unique_id[:6] != secure_hash:
        raise InvalidHash

    file_size = file_id.file_size
    mime_type = (
        file_id.mime_type
        or mimetypes.guess_type(file_name)[0]
        or "application/octet-stream"
    )

    # Parse Range header (supports "bytes=START-END" and "bytes=START-")
    if range_header:
        parts = range_header.replace("bytes=", "").split("-")
        from_bytes  = int(parts[0])
        until_bytes = int(parts[1]) if parts[1] else file_size - 1
    else:
        from_bytes  = 0
        until_bytes = file_size - 1

    req_length     = until_bytes - from_bytes + 1
    chunk_size     = 1024 * 1024          # 1 MiB
    offset         = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut  = (until_bytes % chunk_size) + 1
    part_count     = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    headers = {
        "Content-Type":        mime_type,
        "Content-Range":       f"bytes {from_bytes}-{until_bytes}/{file_size}",
        "Content-Length":      str(req_length),
        "Content-Disposition": f'inline; filename="{file_name}"',
        "Accept-Ranges":       "bytes",
    }

    response = web.StreamResponse(
        status=206 if range_header else 200,
        headers=headers,
    )
    await response.prepare(request)

    # Reuse ByteStreamer per client to avoid spawning a new clean-cache task
    if index not in _byte_streamers:
        _byte_streamers[index] = ByteStreamer(client)
    streamer = _byte_streamers[index]

    async for chunk in streamer.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    ):
        await response.write(chunk)

    return response
