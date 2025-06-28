#!/usr/bin/env python3
"""
Utility script to show current Spusu prices and history
"""

import json
import os
from datetime import datetime


def show_status():
    """Show current prices and history summary"""

    # Check if data files exist
    current_file = "data/spusu_prices.json"
    history_file = "data/price_history.json"

    print("=== SPUSU PRICE MONITOR STATUS ===\n")

    # Show current prices
    if os.path.exists(current_file):
        with open(current_file, "r", encoding="utf-8") as f:
            current_data = json.load(f)

        timestamp = current_data.get("timestamp", "Unknown")
        if timestamp != "Unknown":
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            formatted_time = "Unknown"

        print(f"📊 CURRENT PRICES (Last updated: {formatted_time})")
        print(f"🌐 Source: {current_data.get('source_url', 'Unknown')}")
        print(f"📱 Total plans found: {current_data.get('total_plans', 0)}\n")

        plans = current_data.get("plans", [])
        if plans:
            # Sort plans by price
            sorted_plans = sorted(plans, key=lambda x: x.get("price_chf", 0))

            for plan in sorted_plans:
                name = plan.get("name", "Unknown")
                price = plan.get("price_chf", 0)
                data = plan.get("data_allowance", "Unknown")
                minutes = plan.get("minutes", "Unknown")
                sms = plan.get("sms", "Unknown")
                eu_roaming = plan.get("eu_roaming", "Unknown")
                eu_roaming_minutes = plan.get("eu_roaming_minutes", "Unknown")

                print(f"💰 {name}")
                print(f"   Price: CHF {price}")
                print(f"   Data: {data}")
                print(f"   Minutes: {minutes}")
                print(f"   SMS: {sms}")
                print(f"   EU Roaming: {eu_roaming}")
                print(f"   EU Roaming Minutes: {eu_roaming_minutes}")
                print()

        # Show price changes
        changes = current_data.get("price_changes", [])
        if changes:
            print("🔄 RECENT PRICE CHANGES:")
            for change in changes:
                plan_name = change.get("plan_name", "Unknown")
                if change.get("change") == "NEW_PLAN":
                    print(f"   ✨ NEW: {plan_name} - CHF {change.get('new_price', 0)}")
                else:
                    old_price = change.get("old_price", 0)
                    new_price = change.get("new_price", 0)
                    change_amount = change.get("change", 0)
                    print(
                        f"   📈 CHANGE: {plan_name} - CHF {old_price} → CHF {new_price} ({change_amount:+.2f})"
                    )
            print()
        else:
            print("✅ No price changes detected in last run\n")
    else:
        print("❌ No current price data found. Run the monitor first.\n")

    # Show history summary
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)

        print(f"📈 PRICE HISTORY SUMMARY")
        print(f"📅 Total monitoring days: {len(history)}")

        if history:
            # Show first and last entries
            first_entry = history[0]
            last_entry = history[-1]

            first_date = datetime.fromisoformat(first_entry["timestamp"]).strftime(
                "%Y-%m-%d"
            )
            last_date = datetime.fromisoformat(last_entry["timestamp"]).strftime(
                "%Y-%m-%d"
            )

            print(f"🗓️  First monitoring: {first_date}")
            print(f"🗓️  Last monitoring: {last_date}")

            # Show all dates
            if len(history) > 1:
                print(f"\n📋 All monitoring dates:")
                for entry in history:
                    date = datetime.fromisoformat(entry["timestamp"]).strftime(
                        "%Y-%m-%d"
                    )
                    plans_count = entry.get("total_plans", 0)
                    changes_count = len(entry.get("price_changes", []))
                    print(f"   {date}: {plans_count} plans, {changes_count} changes")
        print()
    else:
        print("❌ No price history found. Run the monitor first.\n")

    print("🚀 To run monitoring: python monitor_spusu_prices.py")
    print("📖 For more info: see README.md")


if __name__ == "__main__":
    show_status()
