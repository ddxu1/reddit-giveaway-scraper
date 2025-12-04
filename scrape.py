import praw
import os
import json
import requests
from datetime import datetime

# -------------------------
# CONFIGURATION
SUBREDDIT = "legendsza"
KEYWORD = "giveaway"

# Get credentials from environment variables (set in GitHub Secrets)
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "giveaway-scraper by u/PositivePapaya123")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

SEEN_POSTS_FILE = "seen_posts.json"
# -------------------------

def load_seen_posts():
    """Load previously seen post IDs from file."""
    if os.path.exists(SEEN_POSTS_FILE):
        try:
            with open(SEEN_POSTS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('posts', []))
        except Exception as e:
            print(f"Error loading seen posts: {e}")
    return set()

def save_seen_posts(seen):
    """Save seen post IDs to file."""
    try:
        with open(SEEN_POSTS_FILE, 'w') as f:
            json.dump({
                'posts': list(seen),
                'last_updated': datetime.utcnow().isoformat()
            }, f, indent=2)
        print(f"Saved {len(seen)} seen posts to {SEEN_POSTS_FILE}")
    except Exception as e:
        print(f"Error saving seen posts: {e}")

def send_discord_notification(post):
    """Send a notification to Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        print("No Discord webhook URL configured, skipping notification")
        return

    # Create a rich embed for Discord
    embed = {
        "title": post.title,
        "url": f"https://reddit.com{post.permalink}",
        "description": (post.selftext[:500] + "...") if len(post.selftext or "") > 500 else (post.selftext or ""),
        "color": 0xFF4500,  # Reddit orange
        "fields": [
            {"name": "Author", "value": f"u/{post.author.name if post.author else '[deleted]'}", "inline": True},
            {"name": "Subreddit", "value": f"r/{post.subreddit.display_name}", "inline": True},
            {"name": "Score", "value": str(post.score), "inline": True}
        ],
        "timestamp": datetime.utcfromtimestamp(post.created_utc).isoformat(),
        "footer": {"text": "Reddit Giveaway Alert"}
    }

    payload = {
        "content": f"🎁 **New Giveaway Found!**",
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✓ Sent Discord notification for: {post.title}")
        else:
            print(f"✗ Discord webhook failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error sending Discord notification: {e}")

def main():
    # Validate required environment variables
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set as environment variables")
        return

    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    # Load previously seen posts
    seen = load_seen_posts()
    print(f"Loaded {len(seen)} previously seen posts")

    new_matches = 0
    print(f"Checking r/{SUBREDDIT} for '{KEYWORD}'...\n")

    try:
        for post in reddit.subreddit(SUBREDDIT).new(limit=100):
            if post.id in seen:
                continue

            seen.add(post.id)

            # Check if post contains keyword
            if KEYWORD.lower() in post.title.lower() or \
               KEYWORD.lower() in (post.selftext or "").lower():
                print("=" * 60)
                print("MATCH FOUND:")
                print(f"Title: {post.title}")
                print(f"URL: https://reddit.com{post.permalink}")
                print(f"Author: u/{post.author.name if post.author else '[deleted]'}")
                print(f"Created: {datetime.utcfromtimestamp(post.created_utc)}")
                print("=" * 60)
                print()

                send_discord_notification(post)
                new_matches += 1

        # Save updated seen posts
        save_seen_posts(seen)

        print(f"\nScan complete. Found {new_matches} new giveaway(s).")

    except Exception as e:
        print(f"Error: {e}")
        # Still save what we've seen so far
        save_seen_posts(seen)
        raise

if __name__ == "__main__":
    main()
