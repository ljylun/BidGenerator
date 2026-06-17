"""
Fetch video transcript/captions via multiple fallback methods.

Cascade:
  1. YouTube Data API v3 captions (requires OAuth for own videos)
  2. yt-dlp auto-subtitle extraction (if installed)
  3. Graceful failure with instructions

Input: video ID or URL
Output: JSON with transcript text, timestamps, language

Usage:
    python execution/fetch_transcript.py dQw4w9WgXcQ
    python execution/fetch_transcript.py "https://youtube.com/watch?v=dQw4w9WgXcQ"
    python execution/fetch_transcript.py VIDEO_ID --format text
    python execution/fetch_transcript.py VIDEO_ID --format segments
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.quota_tracker import consume_quota

TMP_DIR = Path.home() / ".claude" / ".tmp"


def parse_video_id(raw):
    """Extract video ID from URL or direct ID input."""
    raw = raw.strip()

    # Direct video ID (11 characters)
    if re.match(r"^[\w-]{11}$", raw):
        return raw

    # URL patterns
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw)
        if match:
            return match.group(1)

    return raw  # Return as-is, let the API validate


def fetch_via_ytdlp(video_id, lang="en"):
    """Fetch transcript using yt-dlp (fallback method)."""
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        return None, "yt-dlp not installed"

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = str(Path(tmpdir) / "transcript")

        cmd = [
            ytdlp,
            "--skip-download",
            "--write-auto-sub",
            "--sub-lang", lang,
            "--sub-format", "vtt",
            "--output", output_template,
            url,
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired:
            return None, "yt-dlp timed out after 30 seconds"

        # Find the subtitle file
        vtt_files = list(Path(tmpdir).glob("*.vtt"))
        if not vtt_files:
            # Try SRT format as fallback
            cmd[cmd.index("vtt")] = "srt"
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            except subprocess.TimeoutExpired:
                return None, "yt-dlp timed out"

            srt_files = list(Path(tmpdir).glob("*.srt"))
            if not srt_files:
                return None, f"No subtitles found. yt-dlp stderr: {result.stderr[:200]}"

            return parse_srt(srt_files[0].read_text()), None

        return parse_vtt(vtt_files[0].read_text()), None


def parse_vtt(content):
    """Parse WebVTT subtitle content into segments."""
    segments = []
    lines = content.strip().split("\n")
    current_text = []
    current_start = None

    for line in lines:
        line = line.strip()
        # Skip header and empty lines
        if line.startswith("WEBVTT") or line.startswith("Kind:") or \
           line.startswith("Language:") or not line:
            if current_text and current_start:
                text = " ".join(current_text).strip()
                # Remove VTT tags
                text = re.sub(r"<[^>]+>", "", text)
                if text:
                    segments.append({"start": current_start, "text": text})
                current_text = []
            continue

        # Timestamp line
        time_match = re.match(
            r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})", line
        )
        if time_match:
            if current_text and current_start:
                text = " ".join(current_text).strip()
                text = re.sub(r"<[^>]+>", "", text)
                if text:
                    segments.append({"start": current_start, "text": text})
                current_text = []
            current_start = time_match.group(1)
            continue

        # Skip numeric cue identifiers
        if re.match(r"^\d+$", line):
            continue

        current_text.append(line)

    # Last segment
    if current_text and current_start:
        text = " ".join(current_text).strip()
        text = re.sub(r"<[^>]+>", "", text)
        if text:
            segments.append({"start": current_start, "text": text})

    # Deduplicate consecutive identical segments
    deduped = []
    for seg in segments:
        if not deduped or deduped[-1]["text"] != seg["text"]:
            deduped.append(seg)

    return deduped


def parse_srt(content):
    """Parse SRT subtitle content into segments."""
    segments = []
    blocks = re.split(r"\n\n+", content.strip())

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        time_match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})",
            lines[1],
        )
        if time_match:
            start = time_match.group(1).replace(",", ".")
            text = " ".join(lines[2:]).strip()
            text = re.sub(r"<[^>]+>", "", text)
            if text:
                segments.append({"start": start, "text": text})

    return segments


def segments_to_text(segments):
    """Convert segments to plain text."""
    return " ".join(seg["text"] for seg in segments)


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video transcript")
    parser.add_argument("video", help="Video ID or URL")
    parser.add_argument("--lang", default="en", help="Language code (default: en)")
    parser.add_argument("--format", choices=["text", "segments", "both"],
                        default="both", help="Output format (default: both)")

    args = parser.parse_args()

    video_id = parse_video_id(args.video)

    # Check cache
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TMP_DIR / f"transcript_{video_id}_{args.lang}.json"

    if cache_path.exists():
        with open(cache_path) as f:
            cached = json.load(f)
        cached["_cached"] = True
        print(json.dumps(cached, indent=2))
        return

    # Try yt-dlp (most reliable for public videos, no API quota cost)
    segments, error = fetch_via_ytdlp(video_id, args.lang)

    if segments:
        result = {
            "video_id": video_id,
            "language": args.lang,
            "method": "yt-dlp",
            "segment_count": len(segments),
            "fetched_at": datetime.now().isoformat(),
        }

        if args.format in ("segments", "both"):
            result["segments"] = segments
        if args.format in ("text", "both"):
            result["text"] = segments_to_text(segments)

        # Cache
        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)

        print(json.dumps(result, indent=2))
        return

    # All methods failed
    print(json.dumps({
        "error": "Could not fetch transcript",
        "video_id": video_id,
        "attempts": [
            {"method": "yt-dlp", "error": error or "not attempted"},
        ],
        "suggestions": [
            "Install yt-dlp: pip install yt-dlp",
            "Check if the video has captions enabled",
            "Try a different language with --lang",
            "For private videos, ensure OAuth is configured",
        ],
    }, indent=2), file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
