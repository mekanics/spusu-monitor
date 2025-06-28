#!/usr/bin/env python3
"""
Generate detailed Telegram message for Spusu price changes
"""

import json
import sys
from datetime import datetime
import re


def load_current_prices():
    """Load current prices from JSON file"""
    try:
        with open("data/spusu_prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def parse_price_changes(price_changes_file):
    """Parse price changes from the monitoring output"""
    changes = []
    new_plans = []

    try:
        with open(price_changes_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith("CHANGE:"):
                # Extract change details
                change_info = line.replace("CHANGE: ", "")
                # Parse: "plan_name - CHF old_price → CHF new_price (+change)"
                parts = change_info.split(" - CHF ")
                if len(parts) >= 2:
                    plan_name = parts[0].strip()
                    price_part = parts[1]

                    # Extract old and new prices
                    price_match = re.search(
                        r"([0-9.]+) → CHF ([0-9.]+) \(([^)]+)\)", price_part
                    )
                    if price_match:
                        old_price = float(price_match.group(1))
                        new_price = float(price_match.group(2))
                        change_amount = price_match.group(3)

                        # Calculate percentage change
                        percentage = ((new_price - old_price) / old_price) * 100
                        change_str = f"{change_amount} ({percentage:+.1f}%)"

                        changes.append(
                            {
                                "plan_name": plan_name,
                                "old_price": old_price,
                                "new_price": new_price,
                                "change_str": change_str,
                            }
                        )

            elif line.startswith("NEW:"):
                # Extract new plan details
                new_info = line.replace("NEW: ", "")
                # Parse: "plan_name - CHF price"
                parts = new_info.split(" - CHF ")
                if len(parts) >= 2:
                    plan_name = parts[0].strip()
                    price = float(parts[1].strip())

                    new_plans.append({"plan_name": plan_name, "price": price})

    except Exception as e:
        print(f"Error parsing price changes: {e}", file=sys.stderr)

    return changes, new_plans


def get_plan_details(plan_name, current_data):
    """Get detailed plan information from current data"""
    if not current_data or "plans" not in current_data:
        return None

    for plan in current_data["plans"]:
        if (
            plan_name.lower() in plan["name"].lower()
            or plan["name"].lower() in plan_name.lower()
        ):
            return plan

    return None


def format_plan_features(plan):
    """Format plan features for display"""
    features = []

    # Data allowance
    if plan.get("data_allowance") == "unlimited":
        features.append("Unlimited data")
    elif plan.get("data_allowance"):
        features.append(f"{plan['data_allowance']} data")

    # Minutes and SMS
    if plan.get("minutes") == "unlimited" and plan.get("sms") == "unlimited":
        features.append("unlimited calls & SMS")
    elif plan.get("minutes") == "unlimited":
        features.append("unlimited calls")
    elif plan.get("sms") == "unlimited":
        features.append("unlimited SMS")

    return ", ".join(features) if features else "Mobile plan"


def format_eu_roaming(plan):
    """Format EU roaming information"""
    if not plan.get("eu_roaming") or plan["eu_roaming"] == "Unknown":
        return "Included"

    roaming_info = plan["eu_roaming"]
    if plan.get("eu_roaming_minutes") and plan["eu_roaming_minutes"] != "Unknown":
        roaming_info += f" + {plan['eu_roaming_minutes']} min/SMS"

    return roaming_info


def generate_telegram_message(price_changes_file):
    """Generate the formatted Telegram message"""
    current_data = load_current_prices()
    changes, new_plans = parse_price_changes(price_changes_file)

    # Start building the message
    message = "🚨 *Spusu Price Alert* 🚨\n\n"
    message += f"📅 *{datetime.now().strftime('%B %d, %Y at %H:%M')}*\n\n"
    message += "---\n\n"

    # Process price changes
    if changes:
        # Separate increases and decreases
        increases = [c for c in changes if c["new_price"] > c["old_price"]]
        decreases = [c for c in changes if c["new_price"] < c["old_price"]]

        # Handle price increases
        if increases:
            message += "### 📈 *Price Increases*\n\n"

            for change in increases:
                plan_details = get_plan_details(change["plan_name"], current_data)

                # Calculate percentage for warning
                percentage_match = re.search(
                    r"\(([+-][0-9.]+)%\)", change["change_str"]
                )
                warning = ""
                if percentage_match:
                    percentage = abs(float(percentage_match.group(1)))
                    if percentage > 20:
                        warning = " ⚠️ *Significant increase*"

                price_change = change["new_price"] - change["old_price"]
                message += f"🔴 *{change['plan_name']}*\n"
                message += f"• *Price:* CHF {change['old_price']:.2f} → *CHF {change['new_price']:.2f}* (+CHF {price_change:.2f})\n"
                message += f"• *Increase:* {change['change_str']}{warning}\n"

                if plan_details:
                    message += f"• *Features:* {format_plan_features(plan_details)}\n"
                    message += f"• *EU Roaming:* {format_eu_roaming(plan_details)}\n"
                else:
                    message += "• *Features:* Mobile plan with data, calls & SMS\n"
                    message += "• *EU Roaming:* Included\n"

                message += "\n"

            message += "---\n\n"

        # Handle price decreases
        if decreases:
            message += "### 📉 *Price Decreases*\n\n"

            for change in decreases:
                plan_details = get_plan_details(change["plan_name"], current_data)

                # Calculate percentage for significant decrease
                percentage_match = re.search(
                    r"\(([+-][0-9.]+)%\)", change["change_str"]
                )
                warning = ""
                if percentage_match:
                    percentage = abs(float(percentage_match.group(1)))
                    if percentage > 20:
                        warning = " 🎉 *Significant decrease*"

                price_change = abs(change["new_price"] - change["old_price"])
                message += f"🟢 *{change['plan_name']}*\n"
                message += f"• *Price:* CHF {change['old_price']:.2f} → *CHF {change['new_price']:.2f}* (-CHF {price_change:.2f})\n"
                message += f"• *Decrease:* {change['change_str']}{warning}\n"

                if plan_details:
                    message += f"• *Features:* {format_plan_features(plan_details)}\n"
                    message += f"• *EU Roaming:* {format_eu_roaming(plan_details)}\n"
                else:
                    message += "• *Features:* Mobile plan with data, calls & SMS\n"
                    message += "• *EU Roaming:* Included\n"

                message += "\n"

            message += "---\n\n"

    # Process new plans
    if new_plans:
        message += "### ✨ *New Plans Available*\n\n"

        for new_plan in new_plans:
            plan_details = get_plan_details(new_plan["plan_name"], current_data)

            message += f"*🆕 {new_plan['plan_name']}*\n"
            message += f"• *Price:* CHF {new_plan['price']:.2f}\n"

            if plan_details:
                message += f"• *Features:* {format_plan_features(plan_details)}\n"
                message += f"• *EU Roaming:* {format_eu_roaming(plan_details)}\n"
            else:
                message += "• *Features:* Mobile plan with data, calls & SMS\n"
                message += "• *EU Roaming:* Included\n"

            message += "\n"

        message += "---\n\n"

    message += "🔗 [Compare All Plans](https://www.spusu.ch/tariffs)"

    return message


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage: python generate_telegram_message.py <price_changes_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    price_changes_file = sys.argv[1]
    message = generate_telegram_message(price_changes_file)
    print(message)
