"""
Fetch public channel data via YouTube Data API v3.

Uses the uploads playlist path (channels.list → playlistItems.list → videos.list)
to avoid expensive search.list calls. Total cost: ~16 units for channel + 10 videos.

Input: channel ID, handle (@username), or channel URL
Output: JSON with channel stats and top N videos

Usage:
    python execution/fetch_channel_data.py UCxxxxxxxxxxxxxxxx
    python execution/fetch_channel_data.py @channelhandle
    python execution/fetch_channel_data.py "https://youtube.com/@handle"
    python execution/fetch_channel_data.py UCxxx --videos 20
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.quota_tracker import check_quota, consume_quota
from utils.youtube_auth import get_data_api_service

TMP_DIR = Path.home() / ".claude" / ".tmp"


def parse_channel_input(raw):
    """Extract channel ID or handle from various input formats."""
    raw = raw.strip()

    # Direct channel ID
    if raw.startswith("UC") and len(raw) == 24:
        return {"type": "id", "value": raw}

    # Handle format
    if raw.startswith("@"):
        return {"type": "handle", "value": raw}

    # URL formats
    url_patterns = [
        (r"youtube\.com/channel/(UC[\w-]{22})", "id"),
        (r"youtube\.com/@([\w.-]+)", "handle"),
        (r"youtube\.com/c/([\w.-]+)", "custom_url"),
        (r"youtube\.com/user/([\w.-]+)", "username"),
    ]

    for pattern, ptype in url_patterns:
        match = re.search(pattern, raw)
        if match:
            val = match.group(1)
            if ptype == "handle":
                val = f"@{val}"
            return {"type": ptype, "value": val}

    # Assume it's a handle without @
    if not raw.startswith("http"):
        return {"type": "handle", "value": f"@{raw}"}

    return {"type": "unknown", "value": raw}


def resolve_channel_id(service, parsed):
    """Resolve various inputs to a channel ID."""
    if parsed["type"] == "id":
        return parsed["value"]

    if parsed["type"] == "handle":
        response = service.channels().list(
            part="id", forHandle=parsed["value"].lstrip("@")
        ).execute()
        consume_quota("channels.list")
        items = response.get("items", [])
        if items:
            return items[0]["id"]

    if parsed["type"] in ("custom_url", "username"):
        response = service.search().list(
            part="id", q=parsed["value"], type="channel", maxResults=1
        ).execute()
        consume_quota("search.list")
        items = response.get("items", [])
        if items:
            return items[0]["id"]["channelId"]

    return None


def fetch_channel_info(service, channel_id):
    """Fetch channel snippet, statistics, and branding."""
    response = service.channels().list(
        part="snippet,statistics,contentDetails,brandingSettings",
        id=channel_id,
    ).execute()
    consume_quota("channels.list")

    items = response.get("items", [])
    if not items:
        return None

    ch = items[0]
    snippet = ch.get("snippet", {})
    stats = ch.get("statistics", {})
    content = ch.get("contentDetails", {})
    branding = ch.get("brandingSettings", {}).get("channel", {})

    return {
        "channel_id": channel_id,
        "title": snippet.get("title"),
        "description": snippet.get("description", "")[:500],
        "custom_url": snippet.get("customUrl"),
        "published_at": snippet.get("publishedAt"),
        "country": snippet.get("country"),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "uploads_playlist": content.get("relatedPlaylists", {}).get("uploads"),
        "keywords": branding.get("keywords", ""),
    }


def fetch_recent_videos(service, uploads_playlist_id, max_results=10):
    """Fetch recent videos via uploads playlist (cheaper than search.list)."""
    # Step 1: Get video IDs from playlist
    video_ids = []
    next_page = None
    remaining = max_results

    while remaining > 0:
        page_size = min(remaining, 50)
        response = service.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=page_size,
            pageToken=next_page,
        ).execute()
        consume_quota("playlistItems.list")

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
            remaining -= 1
            if remaining <= 0:
                break

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    if not video_ids:
        return []

    # Step 2: Get full video details in batches of 50
    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        response = service.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch),
        ).execute()
        consume_quota("videos.list", len(batch))

        for v in response.get("items", []):
            snippet = v.get("snippet", {})
            stats = v.get("statistics", {})
            content = v.get("contentDetails", {})

            videos.append({
                "video_id": v["id"],
                "title": snippet.get("title"),
                "published_at": snippet.get("publishedAt"),
                "description": snippet.get("description", "")[:200],
                "duration": content.get("duration"),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            })

    return videos


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube channel data")
    parser.add_argument("channel", help="Channel ID, @handle, or URL")
    parser.add_argument("--videos", type=int, default=10,
                        help="Number of recent videos to fetch (default: 10)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Skip cache and fetch fresh data")
    args = parser.parse_args()

    # Check quota before starting
    estimated_cost = 2 + (args.videos // 50 + 1) * 2  # channels + playlist + videos
    quota_check = check_quota("videos.list", estimated_cost)
    if not quota_check.get("can_execute", True):
        print(json.dumps({"error": quota_check["error"]}), file=sys.stderr)
        sys.exit(1)

    # Check cache
    parsed = parse_channel_input(args.channel)
    cache_key = parsed["value"].replace("/", "_").replace("@", "")
    today = datetime.now().strftime("%Y-%m-%d")
    cache_path = TMP_DIR / f"channel_{cache_key}_{today}.json"

    if cache_path.exists() and not args.no_cache:
        with open(cache_path) as f:
            cached = json.load(f)
        cached["_cached"] = True
        print(json.dumps(cached, indent=2))
        return

    # Build service
    service, error = get_data_api_service()
    if error:
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)

    # Resolve channel ID
    channel_id = resolve_channel_id(service, parsed)
    if not channel_id:
        print(json.dumps({"error": f"Could not resolve channel: {args.channel}"}),
              file=sys.stderr)
        sys.exit(1)

    # Fetch data
    channel_info = fetch_channel_info(service, channel_id)
    if not channel_info:
        print(json.dumps({"error": f"Channel not found: {channel_id}"}),
              file=sys.stderr)
        sys.exit(1)

    videos = []
    if channel_info.get("uploads_playlist"):
        videos = fetch_recent_videos(
            service, channel_info["uploads_playlist"], args.videos
        )

    result = {
        "channel": channel_info,
        "videos": videos,
        "fetched_at": datetime.now().isoformat(),
        "quota_consumed": estimated_cost,
    }

    # Cache result
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
