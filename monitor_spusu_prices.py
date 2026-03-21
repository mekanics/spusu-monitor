#!/usr/bin/env python3
"""
Spusu Price Monitor
Monitors mobile plan prices from spusu.ch and tracks price changes over time.
"""

import json
import requests
from datetime import datetime
import os
from typing import Dict, List, Any


class SpusuPriceMonitor:
    def __init__(self):
        self.base_url = "https://www.spusu.ch/de/tariffs"
        self.api_url = "https://www.spusu.ch/imoscmsapi/tariffs/mobile"
        self.data_dir = "data"
        self.price_history_file = os.path.join(self.data_dir, "price_history.json")
        self.current_prices_file = os.path.join(self.data_dir, "spusu_prices.json")

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def _parse_plan(self, sale_item: Dict) -> Dict[str, Any]:
        """Parse a single tariff plan from the IMosCMS API response."""
        tariff = sale_item.get("tariffModel", {})
        fees = tariff.get("fees", {})
        balances = tariff.get("balances", {})

        name = tariff.get("tariffModelName", "Unknown Plan")
        detail_link = sale_item.get("tariffDetailLink", "")
        url = f"{self.base_url}/{detail_link}" if detail_link else self.base_url

        # Price: prefer contractFee, fall back to basicFee
        contract_fee = fees.get("contractFee") or fees.get("basicFee") or {}
        price = contract_fee.get("amount")

        # Data allowance
        nat_data = balances.get("nationalData") or {}
        if nat_data.get("unlimited"):
            data_allowance = "unlimited"
        elif nat_data.get("value") is not None:
            data_allowance = f"{nat_data['value']:.0f}GB"
        else:
            data_allowance = "Unknown"

        # Voice / SMS
        nat_voice = balances.get("nationalVoice") or {}
        minutes = (
            "unlimited"
            if nat_voice.get("unlimited")
            else str(nat_voice.get("value", "Unknown"))
        )

        nat_sms = balances.get("nationalSMS") or {}
        sms = (
            "unlimited"
            if nat_sms.get("unlimited")
            else str(nat_sms.get("value", "Unknown"))
        )

        # EU roaming data
        eu_data = balances.get("euRoamingData") or {}
        if eu_data.get("unlimited"):
            eu_roaming = "unlimited"
        elif eu_data.get("value") is not None:
            eu_roaming = f"{eu_data['value']:.0f}GB"
        else:
            eu_roaming = "0GB"

        # EU roaming voice
        eu_voice = balances.get("euRoamingVoice") or {}
        if eu_voice.get("unlimited"):
            eu_roaming_minutes = "unlimited"
        elif eu_voice.get("value") is not None:
            eu_roaming_minutes = str(int(eu_voice["value"]))
        else:
            eu_roaming_minutes = "Unknown"

        description = tariff.get("balanceAndCostDescription", "")

        return {
            "name": name,
            "price_chf": float(price) if price is not None else None,
            "data_allowance": data_allowance,
            "minutes": minutes,
            "sms": sms,
            "eu_roaming": eu_roaming,
            "eu_roaming_minutes": eu_roaming_minutes,
            "description": description,
            "url": url,
            "scraped_at": datetime.now().isoformat(),
        }

    def scrape_prices(self) -> Dict[str, Any]:
        """Fetch current prices from the Spusu IMosCMS JSON API."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json",
            }

            response = requests.get(self.api_url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            plans = []

            for group in data.get("groups", []):
                for sale_item in group.get("saleItems", []):
                    try:
                        plan = self._parse_plan(sale_item)
                        if plan["price_chf"] is not None and not any(
                            p["name"] == plan["name"] for p in plans
                        ):
                            plans.append(plan)
                    except Exception as e:
                        print(f"Error parsing plan: {e}")
                        continue

            return {
                "timestamp": datetime.now().isoformat(),
                "source_url": self.base_url,
                "plans": plans,
                "total_plans": len(plans),
            }

        except requests.RequestException as e:
            print(f"Error fetching data from {self.api_url}: {e}")
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
                    change_pct = (
                        ((current_price - last_price) / last_price) * 100
                        if last_price
                        else None
                    )
                    changes.append(
                        {
                            "plan_name": plan_name,
                            "old_price": last_price,
                            "new_price": current_price,
                            "change": current_price - last_price,
                            "change_percentage": change_pct,
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

        # Determine if we need to save files
        should_save = False

        if today_entry_index >= 0:
            # There's already an entry for today
            if changes:
                # Only update and save if there are changes
                print(f"Updating existing entry for {today} due to price changes")
                history[today_entry_index] = current_data
                should_save = True
            else:
                print(f"No changes detected, skipping file update for {today}")
        else:
            # First run for today - always save
            print(f"Adding new entry for {today}")
            history.append(current_data)
            should_save = True

        if should_save:
            # Keep only last 2 years of entries to prevent file from growing too large
            if len(history) > 365 * 2:
                history = history[-365 * 2 :]

            # Save files
            self.save_price_history(history)
            self.save_current_prices(current_data)
            print("Files saved successfully")
        else:
            print("No file changes needed")

        print("Monitoring completed successfully")


if __name__ == "__main__":
    monitor = SpusuPriceMonitor()
    monitor.run_monitoring()
