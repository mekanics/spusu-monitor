#!/usr/bin/env python3
"""
Spusu Price Monitor
Monitors mobile plan prices from spusu.ch and tracks price changes over time.
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
from typing import Dict, List, Any


class SpusuPriceMonitor:
    def __init__(self):
        self.base_url = "https://www.spusu.ch/de/tariffs"
        self.data_dir = "data"
        self.price_history_file = os.path.join(self.data_dir, "price_history.json")
        self.current_prices_file = os.path.join(self.data_dir, "spusu_prices.json")

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def scrape_prices(self) -> Dict[str, Any]:
        """Scrape current prices from Spusu website"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = requests.get(self.base_url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            plans = []

            # First, try to find JSON-LD structured data (most reliable method)
            json_ld_scripts = soup.find_all("script", type="application/ld+json")

            for script in json_ld_scripts:
                try:
                    json_data = json.loads(script.string)

                    # Check if it's a graph with products
                    if isinstance(json_data, dict) and "@graph" in json_data:
                        products = json_data["@graph"]
                    elif isinstance(json_data, list):
                        products = json_data
                    elif (
                        isinstance(json_data, dict)
                        and json_data.get("@type") == "Product"
                    ):
                        products = [json_data]
                    else:
                        continue

                    for product in products:
                        if (
                            isinstance(product, dict)
                            and product.get("@type") == "Product"
                        ):
                            name = product.get("name", "Unknown Plan")
                            description = product.get("description", "")

                            # Extract price from offers
                            offers = product.get("offers", {})
                            if isinstance(offers, dict):
                                price = offers.get("price")
                            else:
                                price = None

                            if price is not None:
                                # Parse description for data allowance, minutes, SMS
                                data_allowance = "Unknown"
                                minutes = "Unknown"
                                sms = "Unknown"
                                eu_roaming = "Unknown"

                                if description:
                                    # Extract data allowance
                                    if "unlimitierte GB" in description:
                                        data_allowance = "unlimited"
                                    else:
                                        data_matches = re.findall(
                                            r"(\d+)\s*GB", description
                                        )
                                        if data_matches:
                                            data_allowance = data_matches[0] + "GB"

                                    # Extract minutes
                                    if "unlimitierte Minuten" in description:
                                        minutes = "unlimited"
                                    else:
                                        minutes_matches = re.findall(
                                            r"(\d+)\s*Minuten", description
                                        )
                                        if minutes_matches:
                                            minutes = minutes_matches[0]

                                    # Extract SMS
                                    if (
                                        "unlimitierte" in description
                                        and "SMS" in description
                                    ):
                                        sms = "unlimited"
                                    else:
                                        sms_matches = re.findall(
                                            r"(\d+)\s*SMS", description
                                        )
                                        if sms_matches:
                                            sms = sms_matches[0]

                                    # Extract EU roaming info - split by | and find the EU Roaming part
                                    parts = description.split("|")
                                    eu_part = None
                                    for part in parts:
                                        if "EU Roaming" in part:
                                            eu_part = part.strip()
                                            break

                                    if eu_part:
                                        # Extract the first GB value from the EU Roaming part
                                        eu_match = re.search(
                                            r"(\d+(?:\.\d+)?)\s*GB", eu_part
                                        )
                                        if eu_match:
                                            eu_roaming = eu_match.group(1) + "GB"

                                        # Extract EU roaming minutes
                                        eu_minutes_match = re.search(
                                            r"(\d+(?:\.\d+)?(?:'?\d+)?)\s*Minuten",
                                            eu_part,
                                        )
                                        if eu_minutes_match:
                                            eu_roaming_minutes = eu_minutes_match.group(
                                                1
                                            )
                                        else:
                                            eu_roaming_minutes = "Unknown"
                                    else:
                                        eu_roaming_minutes = "Unknown"

                                plan = {
                                    "name": name,
                                    "price_chf": float(price),
                                    "data_allowance": data_allowance,
                                    "minutes": minutes,
                                    "sms": sms,
                                    "eu_roaming": eu_roaming,
                                    "eu_roaming_minutes": eu_roaming_minutes,
                                    "description": description,
                                    "scraped_at": datetime.now().isoformat(),
                                }

                                # Avoid duplicates
                                if not any(p["name"] == name for p in plans):
                                    plans.append(plan)

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON-LD: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing JSON-LD product: {e}")
                    continue

            # If no plans found with JSON-LD, fall back to HTML scraping
            if not plans:
                print("No plans found with JSON-LD method, trying HTML scraping...")

                # Look for tariff cards or plan containers
                tariff_containers = soup.find_all(
                    ["div", "section"],
                    class_=re.compile(r"tariff|plan|price|card", re.I),
                )

                if not tariff_containers:
                    # Fallback: look for any containers with price information
                    tariff_containers = soup.find_all(
                        string=re.compile(r"CHF|Fr\.", re.I)
                    )
                    tariff_containers = [
                        elem.parent for elem in tariff_containers if elem.parent
                    ]

                for container in tariff_containers[
                    :10
                ]:  # Limit to first 10 to avoid noise
                    try:
                        # Extract plan name
                        name_elem = container.find(
                            ["h1", "h2", "h3", "h4", "strong"],
                            string=re.compile(r"\w+"),
                        )
                        plan_name = (
                            name_elem.get_text(strip=True)
                            if name_elem
                            else "Unknown Plan"
                        )

                        # Extract price
                        price_text = container.get_text()
                        price_matches = re.findall(
                            r"(?:CHF|Fr\.?)\s*(\d+(?:\.\d{2})?)", price_text, re.I
                        )

                        if price_matches:
                            price = float(price_matches[0])

                            # Extract data allowance
                            data_matches = re.findall(
                                r"(\d+(?:\.\d+)?)\s*(?:GB|TB)", price_text, re.I
                            )
                            data_allowance = (
                                data_matches[0] + "GB" if data_matches else "Unknown"
                            )

                            # Extract minutes/SMS info
                            minutes_matches = re.findall(
                                r"(\d+|unlimited|unlimitiert)\s*(?:min|minute)",
                                price_text,
                                re.I,
                            )
                            minutes = (
                                minutes_matches[0] if minutes_matches else "Unknown"
                            )

                            sms_matches = re.findall(
                                r"(\d+|unlimited|unlimitiert)\s*(?:sms)",
                                price_text,
                                re.I,
                            )
                            sms = sms_matches[0] if sms_matches else "Unknown"

                            plan = {
                                "name": plan_name,
                                "price_chf": price,
                                "data_allowance": data_allowance,
                                "minutes": minutes,
                                "sms": sms,
                                "scraped_at": datetime.now().isoformat(),
                            }

                            # Avoid duplicates
                            if not any(
                                p["name"] == plan_name and p["price_chf"] == price
                                for p in plans
                            ):
                                plans.append(plan)

                    except Exception as e:
                        print(f"Error processing container: {e}")
                        continue

            return {
                "timestamp": datetime.now().isoformat(),
                "source_url": self.base_url,
                "plans": plans,
                "total_plans": len(plans),
            }

        except requests.RequestException as e:
            print(f"Error fetching data from {self.base_url}: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "source_url": self.base_url,
                "error": str(e),
                "plans": [],
                "total_plans": 0,
            }
        except Exception as e:
            print(f"Unexpected error during scraping: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "source_url": self.base_url,
                "error": str(e),
                "plans": [],
                "total_plans": 0,
            }

    def load_price_history(self) -> List[Dict]:
        """Load existing price history"""
        try:
            if os.path.exists(self.price_history_file):
                with open(self.price_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading price history: {e}")
            return []

    def save_price_history(self, history: List[Dict]):
        """Save price history to file"""
        try:
            with open(self.price_history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving price history: {e}")

    def save_current_prices(self, current_data: Dict):
        """Save current prices to file"""
        try:
            with open(self.current_prices_file, "w", encoding="utf-8") as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving current prices: {e}")

    def detect_price_changes(
        self, current_data: Dict, history: List[Dict]
    ) -> List[Dict]:
        """Detect price changes compared to last entry"""
        changes = []

        if not history or not history[-1].get("plans"):
            return changes

        last_entry = history[-1]
        last_plans = {plan["name"]: plan for plan in last_entry.get("plans", [])}
        current_plans = {plan["name"]: plan for plan in current_data.get("plans", [])}

        for plan_name, current_plan in current_plans.items():
            if plan_name in last_plans:
                last_price = last_plans[plan_name]["price_chf"]
                current_price = current_plan["price_chf"]

                if last_price != current_price:
                    changes.append(
                        {
                            "plan_name": plan_name,
                            "old_price": last_price,
                            "new_price": current_price,
                            "change": current_price - last_price,
                            "change_percentage": (
                                (current_price - last_price) / last_price
                            )
                            * 100,
                            "detected_at": datetime.now().isoformat(),
                        }
                    )
            else:
                # New plan detected
                changes.append(
                    {
                        "plan_name": plan_name,
                        "old_price": None,
                        "new_price": current_plan["price_chf"],
                        "change": "NEW_PLAN",
                        "change_percentage": None,
                        "detected_at": datetime.now().isoformat(),
                    }
                )

        return changes

    def run_monitoring(self):
        """Main monitoring function"""
        print(f"Starting Spusu price monitoring at {datetime.now()}")

        # Scrape current prices
        current_data = self.scrape_prices()

        if current_data.get("error"):
            print(f"Error occurred during scraping: {current_data['error']}")
            return

        print(f"Found {current_data['total_plans']} plans")

        # Load existing history
        history = self.load_price_history()

        # Detect changes
        changes = self.detect_price_changes(current_data, history)

        if changes:
            print("Price changes detected:")
            for change in changes:
                if change["change"] == "NEW_PLAN":
                    print(f"  NEW: {change['plan_name']} - CHF {change['new_price']}")
                else:
                    print(
                        f"  CHANGE: {change['plan_name']} - CHF {change['old_price']} → CHF {change['new_price']} ({change['change']:+.2f})"
                    )
        else:
            print("No price changes detected")

        # Add current data to history (only one entry per day)
        current_data["price_changes"] = changes
        today = datetime.now().date().isoformat()

        # Check if there's already an entry for today
        today_entry_index = -1
        for i, entry in enumerate(history):
            entry_date = datetime.fromisoformat(entry["timestamp"]).date().isoformat()
            if entry_date == today:
                today_entry_index = i
                break

        if today_entry_index >= 0:
            # Update existing entry for today
            print(f"Updating existing entry for {today}")
            history[today_entry_index] = current_data
        else:
            # Add new entry for today
            print(f"Adding new entry for {today}")
            history.append(current_data)

        # Keep only last 2 years of entries to prevent file from growing too large
        if len(history) > 365 * 2:
            history = history[-365 * 2 :]

        # Save files
        self.save_price_history(history)
        self.save_current_prices(current_data)

        print("Monitoring completed successfully")


if __name__ == "__main__":
    monitor = SpusuPriceMonitor()
    monitor.run_monitoring()
