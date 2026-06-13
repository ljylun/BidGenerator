"""
Search YouTube for videos by topic or from a competitor channel.

Uses YouTube Data API v3 search.list (100 units per call — use sparingly).
For competitor channel videos, prefer using the uploads playlist path via
fetch_channel_data.py which costs only ~16 units instead of 100.

Note: Private metrics (retention, CTR, revenue) are NOT accessible for
competitor channels via any official API. Only public data is returned.

Input: search query or channel ID filter
Output: JSON array of videos with public metrics

Usage:
    python execution/search_competitor_videos.py "python tutorial 2025"
    python execution/search_competitor_videos.py --channel-id UCxxxx --max-results 20
    python execution/search_competitor_videos.py "cooking tips" --order viewCount
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.quota_tracker import check_quota, consume_quota
from utils.youtube_auth import get_data_api_service

TMP_DIR = Path.home() / ".claude" / ".tmp"


def search_videos(service, query, channel_id=None, max_results=10,
                  order="relevance", published_after=None):
    """Search for videos with optional channel filter."""
    search_params = {
        "part": "id,snippet",
        "q": query,
        "type": "video",
        "maxResults": min(max_results, 50),
        "order": order,
    }

    if channel_id:
        search_params["channelId"] = channel_id

    if published_after:
        search_params["publishedAfter"] = published_after

    response = service.search().list(**search_params).execute()
    consume_quota("search.list")

    video_ids = []
    snippets = {}

    for item in response.get("items", []):
        vid = item["id"]["videoId"]
        video_ids.append(vid)
        snippets[vid] = item["snippet"]

    if not video_ids:
        return []

    # Fetch full statistics for found videos (1 unit per batch of 50)
    stats_response = service.videos().list(
        part="statistics,contentDetails",
        id=",".join(video_ids),
    ).execute()
    consume_quota("videos.list", len(video_ids))

    stats_map = {}
    for v in stats_response.get("items", []):
        stats_map[v["id"]] = {
            "statistics": v.get("statistics", {}),
            "content_details": v.get("contentDetails", {}),
        }

    # Combine data
    results = []
    for vid in video_ids:
        snippet = snippets.get(vid, {})
        data = stats_map.get(vid, {})
        stats = data.get("statistics", {})
        content = data.get("content_details", {})

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        engagement_rate = 0
        if views > 0:
            engagement_rate = round((likes + comments) / views * 100, 2)

        results.append({
            "video_id": vid,
            "title": snippet.get("title"),
            "channel_title": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "published_at": snippet.get("publishedAt"),
            "description": snippet.get("description", "")[:200],
            "duration": content.get("duration"),
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate_pct": engagement_rate,
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        })

    return results


def flag_outliers(videos, multiplier=3.0):
    """Flag videos that significantly outperform the channel average."""
    if not videos:
        return videos

    # Group by channel
    channels = {}
    for v in videos:
        ch = v.get("channel_id", "unknown")
        channels.setdefault(ch, []).append(v)

    for ch_id, ch_videos in channels.items():
        if len(ch_videos) < 3:
            continue

        avg_views = sum(v["views"] for v in ch_videos) / len(ch_videos)

        for v in ch_videos:
            if avg_views > 0:
                ratio = v["views"] / avg_views
                v["vs_channel_avg"] = round(ratio, 1)
                v["is_outlier"] = ratio >= multiplier
            else:
                v["vs_channel_avg"] = 0
                v["is_outlier"] = False

    return videos


def main():
    parser = argparse.ArgumentParser(description="Search YouTube competitor videos")
    parser.add_argument("query", nargs="?", default="",
                        help="Search query")
    parser.add_argument("--channel-id", type=str,
                        help="Filter to specific channel")
    parser.add_argument("--max-results", type=int, default=10,
                        help="Max results (default: 10, max: 50)")
    parser.add_argument("--order", choices=["relevance", "viewCount", "date", "rating"],
                        default="relevance", help="Sort order")
    parser.add_argument("--days", type=int, default=None,
                        help="Only videos from last N days")
    parser.add_argument("--flag-outliers", action="store_true",
                        help="Flag videos that outperform channel average by 3x+")

    args = parser.parse_args()

    if not args.query and not args.channel_id:
        parser.error("Provide a search query or --channel-id")

    # Quota check — search.list costs 100 units
    quota_status = check_quota("search.list")
    if not quota_status.get("can_execute", True):
        print(json.dumps({
            "error": quota_status["error"],
            "suggestion": "Use fetch_channel_data.py instead (~16 units) "
                          "if you just need a channel's recent videos.",
        }), file=sys.stderr)
        sys.exit(1)

    remaining = quota_status.get("remaining", 10000)
    if remaining < 200:
        print(json.dumps({
            "warning": f"Only {remaining} quota units remaining. "
                       f"This search costs 100+ units. Proceed with caution.",
        }), file=sys.stderr)

    # Build service
    service, error = get_data_api_service()
    if error:
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)

    # Date filter
    published_after = None
    if args.days:
        dt = datetime.now() - timedelta(days=args.days)
        published_after = dt.strftime("%Y-%m-%dT00:00:00Z")

    # Search
    videos = search_videos(
        service,
        query=args.query,
        channel_id=args.channel_id,
        max_results=args.max_results,
        order=args.order,
        published_after=published_after,
    )

    if args.flag_outliers:
        videos = flag_outliers(videos)

    # Sort by views descending
    videos.sort(key=lambda v: v["views"], reverse=True)

    result = {
        "query": args.query,
        "channel_filter": args.channel_id,
        "result_count": len(videos),
        "videos": videos,
        "fetched_at": datetime.now().isoformat(),
        "note": "Only public metrics shown. Retention, CTR, and revenue "
                "data are private and not accessible for competitor channels.",
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
