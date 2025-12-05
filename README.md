# Reddit Giveaway Scraper for Discord

Automatically scrapes multiple Pokemon-related subreddits for giveaway posts and sends notifications to Discord via webhook. Runs for free on GitHub Actions every 15 minutes.

## Features

- 🔄 Runs automatically every 15 minutes on GitHub Actions
- 🎁 Monitors multiple subreddits with custom search criteria
- 📢 Sends rich Discord notifications with post details
- 💾 Tracks seen posts to avoid duplicate notifications
- 🆓 Completely free using GitHub Actions

## Search Criteria

The scraper monitors the following subreddits with specific filters:

1. **r/PokemonLegendsZa**
   - Searches for: "giveaway" (case insensitive)
   - Checks: Post titles and body text
   - Flair filter: None

2. **r/LegendsZa**
   - Searches for: "giveaway" (case insensitive)
   - Checks: Post titles and body text
   - Flair filter: None

3. **r/PokemonZA**
   - Searches for: "giveaway" (case insensitive) OR "Shiny Giveaway" flair
   - Checks: Post titles and body text for keyword, OR post flair
   - Logic: Matches if EITHER condition is met

4. **r/ShinyPokemon**
   - Searches for: Posts containing BOTH "9]" AND "giveaway" (case insensitive)
   - Checks: Post titles only
   - Flair filter: None

## Setup Instructions

### 1. Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - Name: `giveaway-scraper`
   - App type: Select "script"
   - Description: (optional)
   - About URL: (leave blank)
   - Redirect URI: `http://localhost:8080`
4. Click "Create app"
5. Note your `client_id` (under the app name) and `client_secret`

### 2. Create Discord Webhook

1. Open your Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Give it a name (e.g., "Giveaway Bot") and select the channel
5. Click "Copy Webhook URL"

### 3. Fork/Upload This Repository to GitHub

1. Create a new GitHub repository or fork this one
2. Upload all files to your repository

### 4. Configure GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret" and add the following secrets:

   - `REDDIT_CLIENT_ID`: Your Reddit app client ID
   - `REDDIT_CLIENT_SECRET`: Your Reddit app client secret
   - `   `: Something like `giveaway-scraper by u/YourRedditUsername`
   - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL

### 5. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. If prompted, enable GitHub Actions
3. The workflow will run automatically every 15 minutes
4. You can also manually trigger it by clicking "Run workflow"

### 6. Verify It's Working

1. Go to Actions tab → Click on "Reddit Giveaway Scraper"
2. Check the latest workflow run
3. View the logs to see if posts were found

## Configuration

Edit the `SUBREDDIT_CONFIGS` list in `scrape.py` to customize subreddit monitoring:

Each subreddit configuration supports:
- `subreddit`: The subreddit name to monitor
- `keyword`: Search term to find in posts (case insensitive)
- `flair`: Specific post flair/tag to filter by (must match exactly)
- `custom_filter`: Special custom filtering logic for advanced use cases

You can add, remove, or modify subreddit configurations as needed.

Edit `.github/workflows/reddit-scraper.yml` to customize:

- Cron schedule: Change `*/15 * * * *` to run more/less frequently
  - `*/10 * * * *` = every 10 minutes
  - `*/30 * * * *` = every 30 minutes
  - `0 * * * *` = every hour

## How It Works

1. GitHub Actions runs the scraper every 15 minutes
2. The script checks the latest 100 posts in each configured subreddit
3. Posts matching the specific criteria for each subreddit trigger a Discord notification
4. Post IDs are saved to `seen_posts.json` to prevent duplicates
5. The file is committed back to the repository

## Files

- `scrape.py`: Main scraper script
- `requirements.txt`: Python dependencies
- `.github/workflows/reddit-scraper.yml`: GitHub Actions workflow
- `seen_posts.json`: Tracks seen posts (auto-generated)

## Troubleshooting

**No notifications appearing:**
- Check the Actions tab for error logs
- Verify all secrets are set correctly
- Ensure Discord webhook URL is valid

**Duplicate notifications:**
- Make sure `seen_posts.json` is being committed back to the repository
- Check that git push permissions are working

**Rate limiting:**
- Reddit API allows ~60 requests per minute for free
- Current setup is well within limits

## Local Testing

To test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="test by u/YourUsername"
export DISCORD_WEBHOOK_URL="your_webhook_url"

# Run the scraper
python scrape.py
```

## License

MIT - Feel free to modify and use for your own purposes!
