# Spusu Price Monitor

> **Note**: This repository has been created for learning purposes to learn how to use GitHub Actions as a workflow and try out automated monitoring. The code was generated with the assistance of AI. 🤖

This project monitors mobile plan prices from [Spusu Switzerland](https://www.spusu.ch/de/tariffs) and tracks price changes over time.

## Features

- **Daily Monitoring**: Automatically scrapes prices once per day using GitHub Actions
- **Price History**: Maintains a complete history of price changes in `data/price_history.json`
- **Current Prices**: Stores the latest prices in `data/spusu_prices.json`
- **Change Detection**: Identifies when prices change and logs the differences
- **Telegram Notifications**: Sends instant notifications when prices change (optional)
- **Robust Scraping**: Handles various HTML structures and provides fallback methods

## Telegram Channel

📢 **Join our Telegram channel for price alerts**: [@spusu_price_alerts](https://t.me/spusu_price_alerts)

Get instant notifications whenever Spusu plan prices change!

## Files

- `monitor_spusu_prices.py` - Main Python script for price monitoring
- `show_status.py` - Utility script to display current prices and history
- `requirements.txt` - Python dependencies
- `.github/workflows/monitor-prices.yml` - GitHub Actions workflow with Telegram notifications
- `data/price_history.json` - Historical price data (one entry per day)
- `data/spusu_prices.json` - Current price data
- `TELEGRAM_SETUP.md` - Guide for setting up Telegram notifications

## Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd spusu-monitor
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run manually (optional)**

   ```bash
   python monitor_spusu_prices.py
   ```

4. **Check status**

   ```bash
   python show_status.py
   ```

5. **Enable GitHub Actions**

   - The workflow will automatically run daily at 8:00 AM UTC
   - You can also trigger it manually from the Actions tab

6. **Set up Telegram notifications (optional)**
   - Follow the guide in `TELEGRAM_SETUP.md` to receive instant notifications when prices change
   - Requires creating a Telegram bot and configuring GitHub secrets

## How it Works

1. **Web Scraping**: The script visits the Spusu tariffs page and extracts plan information
2. **Data Extraction**: It looks for plan names, prices, data allowances, minutes, and SMS limits
3. **Change Detection**: Compares current prices with the last recorded prices
4. **Data Storage**: Saves both historical data and current prices in JSON format
5. **Automated Updates**: GitHub Actions commits any changes back to the repository

## Data Structure

### Price History (`data/price_history.json`)

```json
[
  {
    "timestamp": "2024-01-15T08:00:00",
    "source_url": "https://www.spusu.ch/de/tariffs",
    "plans": [
      {
        "name": "Plan Name",
        "price_chf": 25.0,
        "data_allowance": "10GB",
        "minutes": "unlimited",
        "sms": "unlimited",
        "scraped_at": "2024-01-15T08:00:00"
      }
    ],
    "total_plans": 1,
    "price_changes": []
  }
]
```

### Current Prices (`data/spusu_prices.json`)

Contains the most recent price data in the same format as individual history entries.
