"""
YouTube API authentication manager.

Handles API key auth for public Data API v3 and OAuth 2.0 for Analytics API.
Input: auth_type ('api_key' | 'oauth'), optional credentials path
Output: authenticated googleapiclient service object OR error dict

Usage:
    python execution/utils/youtube_auth.py --check api_key
    python execution/utils/youtube_auth.py --check oauth
"""

import argparse
import json
import os
import sys
from pathlib import Path

TMP_DIR = Path.home() / ".claude" / ".tmp"
TOKEN_PATH = TMP_DIR / "youtube_oauth_token.json"
CLIENT_SECRETS_PATH = Path.home() / ".claude" / "youtube_client_secrets.json"


def get_api_key():
    """Return YouTube Data API v3 key from environment or config file."""
    key = os.environ.get("YOUTUBE_API_KEY")
    if key:
        return key

    config_path = Path.home() / ".claude" / "youtube-credentials.json"
    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
            key = data.get("api_key")
            if key:
                return key

    return None


def get_data_api_service(api_key=None):
    """Build and return YouTube Data API v3 service object."""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        return None, {
            "error": "google-api-python-client not installed",
            "fix": "pip install google-api-python-client google-auth-oauthlib",
        }

    if api_key is None:
        api_key = get_api_key()

    if not api_key:
        return None, {
            "error": "YouTube API key not found",
            "fix": (
                "Set YOUTUBE_API_KEY environment variable or add to "
                "~/.claude/youtube-credentials.json as {\"api_key\": \"YOUR_KEY\"}. "
                "Get a key at https://console.cloud.google.com/apis/credentials"
            ),
        }

    try:
        service = build("youtube", "v3", developerKey=api_key)
        return service, None
    except Exception as e:
        return None, {"error": f"Failed to build YouTube service: {e}"}


def get_oauth_service(scopes=None):
    """Build YouTube Analytics API service with OAuth 2.0."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        return None, {
            "error": "OAuth dependencies not installed",
            "fix": "pip install google-api-python-client google-auth-oauthlib",
        }

    if scopes is None:
        scopes = [
            "https://www.googleapis.com/auth/yt-analytics.readonly",
            "https://www.googleapis.com/auth/youtube.readonly",
        ]

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    creds = None

    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), scopes)
        except Exception:
            creds = None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if not CLIENT_SECRETS_PATH.exists():
            return None, {
                "error": "OAuth client secrets not found",
                "fix": (
                    f"Download OAuth 2.0 client secrets from Google Cloud Console "
                    f"and save to {CLIENT_SECRETS_PATH}. "
                    f"Guide: https://developers.google.com/youtube/analytics/registering_an_application"
                ),
            }

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_PATH), scopes
            )
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
        except Exception as e:
            return None, {"error": f"OAuth flow failed: {e}"}

    try:
        service = build("youtubeAnalytics", "v2", credentials=creds)
        return service, None
    except Exception as e:
        return None, {"error": f"Failed to build Analytics service: {e}"}


def check_auth(auth_type):
    """Check if authentication is configured and return status."""
    if auth_type == "api_key":
        key = get_api_key()
        if key:
            masked = key[:4] + "..." + key[-4:]
            return {"status": "ok", "type": "api_key", "key": masked}
        return {"status": "missing", "type": "api_key",
                "fix": "Set YOUTUBE_API_KEY env var or add to ~/.claude/youtube-credentials.json"}

    elif auth_type == "oauth":
        if TOKEN_PATH.exists():
            return {"status": "ok", "type": "oauth", "token_path": str(TOKEN_PATH)}
        if CLIENT_SECRETS_PATH.exists():
            return {"status": "needs_auth", "type": "oauth",
                    "message": "Client secrets found but no token yet. Run OAuth flow."}
        return {"status": "missing", "type": "oauth",
                "fix": f"Download OAuth client secrets to {CLIENT_SECRETS_PATH}"}

    return {"status": "error", "message": f"Unknown auth type: {auth_type}"}


def main():
    parser = argparse.ArgumentParser(description="YouTube API auth manager")
    parser.add_argument("--check", choices=["api_key", "oauth"],
                        help="Check auth status")
    args = parser.parse_args()

    if args.check:
        result = check_auth(args.check)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] == "ok" else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
