# Telegram Notifications Setup

This guide explains how to set up Telegram notifications for Spusu price changes.

## Prerequisites

1. A Telegram account
2. Access to your GitHub repository settings

## Step 1: Create a Telegram Bot

1. **Start a chat with @BotFather** on Telegram
2. **Send `/newbot`** command
3. **Choose a name** for your bot (e.g., "Spusu Price Monitor")
4. **Choose a username** for your bot (e.g., "spusu_price_monitor_bot")
5. **Save the Bot Token** - you'll get something like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Get Your Chat ID

### Option A: Personal Chat

1. **Start a chat** with your new bot
2. **Send any message** to the bot
3. **Visit this URL** in your browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. **Find your chat ID** in the response - look for `"chat":{"id":123456789}`

### Option B: Group Chat

1. **Add your bot** to a Telegram group
2. **Send a message** mentioning the bot (e.g., "@your_bot_name hello")
3. **Visit the getUpdates URL** (same as above)
4. **Find the group chat ID** - it will be negative (e.g., `-123456789`)

### Option C: Public Channel/Group (Bot-Only Posting)

For a **public channel or group where only the bot can post**:

1. **Create a new Telegram channel or group:**

   - Open Telegram and create a new channel (for broadcast-only) or group
   - Make it **public** and set a username (e.g., `@spusu_price_alerts`)
   - Add a description like "Spusu mobile plan price monitoring alerts"

2. **Add your bot as an administrator:**

   - Go to channel/group settings → Administrators
   - Add your bot by searching for its username
   - **For channels**: Give the bot "Post Messages" permission
   - **For groups**: Give the bot "Delete Messages" and "Pin Messages" permissions, and consider restricting other members' posting rights

3. **Restrict member posting (for groups only):**

   - Go to group settings → Permissions
   - Turn off "Send Messages" for members
   - This ensures only administrators (including your bot) can post

4. **Get the channel/group ID:**

   - Send a message to the channel/group (you can delete it later)
   - Visit the getUpdates URL: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
   - Find the chat ID - it will be negative (e.g., `-100123456789` for supergroups/channels)

5. **Test the setup:**
   - Use the curl command below to test if the bot can post

## Step 3: Configure GitHub Secrets

1. **Go to your GitHub repository**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add the following repository secrets:**

   - **`TELEGRAM_BOT_TOKEN`**

     - Value: Your bot token from Step 1 (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

   - **`TELEGRAM_CHAT_ID`**
     - Value: Your chat ID from Step 2 (e.g., `123456789` or `-123456789`)

## Step 4: Test the Setup

1. **Trigger the workflow manually:**

   - Go to Actions tab in your GitHub repository
   - Select "Monitor Spusu Prices" workflow
   - Click "Run workflow"

2. **Or wait for a scheduled run** (daily at 8:00 AM UTC)

3. **Check if notifications work** when price changes are detected

## Notification Format

When price changes are detected, you'll receive a Telegram message like:

```
🚨 Spusu Price Changes Detected 🚨

📅 Date: 2024-01-15 08:30:45

✨ NEW: spusu 25 - CHF 15.90
📈 CHANGE: spusu 10 - CHF 9.90 → CHF 8.90 (-1.00)

🔗 View Details
```

## Troubleshooting

### Bot Token Issues

- Make sure the token is correct and complete
- Ensure there are no extra spaces in the GitHub secret

### Chat ID Issues

- For personal chats: positive number (e.g., `123456789`)
- For group chats: negative number (e.g., `-123456789`)
- For channels/supergroups: negative number starting with `-100` (e.g., `-100123456789`)
- Make sure you've sent at least one message to the bot/group/channel
- For channels: ensure the bot has admin rights with "Post Messages" permission

### No Notifications

- Check GitHub Actions logs for errors
- Verify both secrets are set correctly
- Ensure the bot hasn't been blocked

### Testing the Bot Manually

You can test your bot configuration with curl:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<YOUR_CHAT_ID>",
    "text": "Test message from Spusu Price Monitor 🤖"
  }'
```

## Security Notes

- **Never commit** bot tokens or chat IDs to your repository
- **Use GitHub Secrets** for all sensitive information
- **Regenerate tokens** if they're accidentally exposed
