import json
import re
import urllib.request
from urllib.parse import urlparse, parse_qs


def extract_youtube_id(url: str) -> str:
    """
    Accept any YouTube URL form or a bare 11-char ID and return the video ID.
    Returns empty string if nothing recognizable is found.
    """
    if not url:
        return ''
    url = url.strip()
    # youtu.be/ID
    m = re.match(r'(?:https?://)?youtu\.be/([A-Za-z0-9_-]{11})', url)
    if m:
        return m.group(1)
    # youtube.com/watch?v=ID or /embed/ID or /shorts/ID
    m = re.match(r'(?:https?://)?(?:www\.)?youtube\.com/(?:watch\?.*v=|embed/|shorts/)([A-Za-z0-9_-]{11})', url)
    if m:
        return m.group(1)
    # bare ID — exactly 11 alphanumeric/dash/underscore chars
    if re.match(r'^[A-Za-z0-9_-]{11}$', url):
        return url
    return ''


def fetch_bandcamp_embed(url: str) -> str:
    """
    Build a Bandcamp iframe by scraping the album/track ID from the page's
    og:video meta tag. Falls back to the oEmbed API, then gives up.
    """
    if not url:
        return ''
    url = url.strip()
    # Determine if album or track
    kind = 'track' if '/track/' in url else 'album'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode('utf-8', errors='replace')
        # Extract numeric ID from the EmbeddedPlayer meta tag
        m = re.search(rf'EmbeddedPlayer[^"\']*/{kind}=(\d+)', html)
        if m:
            item_id = m.group(1)
            return (
                f'<iframe style="border:0;width:100%;height:120px;" '
                f'src="https://bandcamp.com/EmbeddedPlayer/{kind}={item_id}/size=small/bgcol=ffffff/linkcol=b8965a/transparent=true/" '
                f'seamless><a href="{url}">Listen on Bandcamp</a></iframe>'
            )
    except Exception:
        pass
    # Fallback: oEmbed
    try:
        oembed = f'https://bandcamp.com/oembed?url={url}&format=json'
        req = urllib.request.Request(oembed, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read()).get('html', '')
    except Exception:
        return ''
