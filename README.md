# Spusu Price Monitor

This project monitors mobile plan prices from [Spusu Switzerland](https://www.spusu.ch/de/tariffs) and tracks price changes over time.

## Features

- **Daily Monitoring**: Automatically scrapes prices once per day using GitHub Actions
- **Price History**: Maintains a complete history of price changes in `data/price_history.json`
- **Current Prices**: Stores the latest prices in `data/spusu_prices.json`
- **Change Detection**: Identifies when prices change and logs the differences
- **Robust Scraping**: Handles various HTML structures and provides fallback methods

## Files

- `monitor_spusu_prices.py` - Main Python script for price monitoring
- `requirements.txt` - Python dependencies
- `.github/workflows/monitor-prices.yml` - GitHub Actions workflow
- `data/price_history.json` - Historical price data
- `data/spusu_prices.json` - Current price data

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

4. **Enable GitHub Actions**
   - The workflow will automatically run daily at 8:00 AM UTC
   - You can also trigger it manually from the Actions tab

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

## Monitoring

The system automatically:

- Runs daily via GitHub Actions
- Detects price changes
- Commits updates to the repository
- Maintains a rolling history of the last 100 monitoring sessions

## Troubleshooting

If the scraper stops working, it might be due to:

1. **Website structure changes** - The HTML structure of the Spusu website may have changed
2. **Rate limiting** - The website might be blocking automated requests
3. **Network issues** - Temporary connectivity problems

Check the GitHub Actions logs for detailed error messages.

## Contributing

Feel free to improve the scraping logic or add new features. The scraper is designed to be robust but may need adjustments if the website structure changes significantly.
