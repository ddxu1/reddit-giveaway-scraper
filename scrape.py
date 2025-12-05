import praw
import os
import json
import requests
from datetime import datetime

# -------------------------
# CONFIGURATION
# Define subreddits with their specific search criteria
SUBREDDIT_CONFIGS = [
    {
        "subreddit": "PokemonLegendsZa",
        "keyword": "giveaway",
        "flair": None,
        "custom_filter": None
    },
    {
        "subreddit": "LegendsZa",
        "keyword": "giveaway",
        "flair": None,
        "custom_filter": None
    },
    {
        "subreddit": "PokemonZA",
        "keyword": "giveaway",
        "flair": "Shiny Giveaway",
        "custom_filter": "pokemonza_or"  # Match keyword OR flair
    },
    {
        "subreddit": "ShinyPokemon",
        "keyword": None,
        "flair": None,
        "custom_filter": "shinypokemon_gen9"  # Special filter for gen 9 giveaways
    }
]

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
    fields = [
        {"name": "Author", "value": f"u/{post.author.name if post.author else '[deleted]'}", "inline": True},
        {"name": "Subreddit", "value": f"r/{post.subreddit.display_name}", "inline": True},
        {"name": "Score", "value": str(post.score), "inline": True}
    ]

    # Add flair if present
    if post.link_flair_text:
        fields.append({"name": "Flair", "value": post.link_flair_text, "inline": True})

    embed = {
        "title": post.title,
        "url": f"https://reddit.com{post.permalink}",
        "description": (post.selftext[:500] + "...") if len(post.selftext or "") > 500 else (post.selftext or ""),
        "color": 0xFF4500,  # Reddit orange
        "fields": fields,
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

def matches_criteria(post, config):
    """Check if a post matches the given subreddit configuration criteria."""
    # Handle custom filters
    if config["custom_filter"] == "shinypokemon_gen9":
        # Check for "9]" and "giveaway" in title
        title_lower = post.title.lower()
        return "9]" in post.title and "giveaway" in title_lower

    if config["custom_filter"] == "pokemonza_or":
        # Check for "giveaway" keyword OR "Shiny Giveaway" flair
        has_keyword = False
        if config["keyword"]:
            keyword_lower = config["keyword"].lower()
            has_keyword = (keyword_lower in post.title.lower() or
                          keyword_lower in (post.selftext or "").lower())

        has_flair = config["flair"] and post.link_flair_text == config["flair"]

        return has_keyword or has_flair

    # Check flair if specified (AND logic)
    if config["flair"] and post.link_flair_text != config["flair"]:
        return False

    # Check keyword if specified
    if config["keyword"]:
        keyword_lower = config["keyword"].lower()
        return (keyword_lower in post.title.lower() or
                keyword_lower in (post.selftext or "").lower())

    return False

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

    total_matches = 0

    # Process each subreddit configuration
    for config in SUBREDDIT_CONFIGS:
        subreddit_name = config["subreddit"]
        keyword = config["keyword"]
        flair = config["flair"]
        custom_filter = config["custom_filter"]

        # Build description message
        if custom_filter == "shinypokemon_gen9":
            criteria = "posts with '9]' and 'giveaway' in title"
        elif custom_filter == "pokemonza_or":
            criteria = f"'{keyword}' OR flair '{flair}'"
        elif flair and keyword:
            criteria = f"'{keyword}' with flair '{flair}'"
        elif flair:
            criteria = f"posts with flair '{flair}'"
        elif keyword:
            criteria = f"'{keyword}'"
        else:
            criteria = "posts"

        print(f"Checking r/{subreddit_name} for {criteria}...\n")

        try:
            for post in reddit.subreddit(subreddit_name).new(limit=100):
                if post.id in seen:
                    continue

                seen.add(post.id)

                # Check if post matches criteria
                if matches_criteria(post, config):
                    print("=" * 60)
                    print("MATCH FOUND:")
                    print(f"Subreddit: r/{subreddit_name}")
                    print(f"Title: {post.title}")
                    print(f"Flair: {post.link_flair_text or '[none]'}")
                    print(f"URL: https://reddit.com{post.permalink}")
                    print(f"Author: u/{post.author.name if post.author else '[deleted]'}")
                    print(f"Created: {datetime.utcfromtimestamp(post.created_utc)}")
                    print("=" * 60)
                    print()

                    send_discord_notification(post)
                    total_matches += 1

        except Exception as e:
            print(f"Error checking r/{subreddit_name}: {e}")
            continue

    # Save updated seen posts
    save_seen_posts(seen)

    print(f"\nScan complete. Found {total_matches} new giveaway(s) across all subreddits.")

if __name__ == "__main__":
    main()
