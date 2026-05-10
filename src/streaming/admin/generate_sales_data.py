"""src/streaming/admin/generate_sales_data.py.

Generate simulated sales data.

Generates approximately 178 sale records spanning 3 days with patterns
worth finding:

  - Time-of-day variation (busy lunch and evenings, quiet overnight)
  - Day 2: SPRING25 promotion launches at 11am
      - Order volume spikes (~45 orders in one afternoon window)
      - New customer rate jumps from ~15% to ~60%
      - Mobile device share increases
      - Social and email referrals increase
  - Day 3: Post-promotion tail-off
  - PY-STREAM-005 trending upward across all three days

Output: data/sales.csv

Run from the root project folder:

    uv run python -m streaming.admin.generate_sales_data

OBS:
  Re-run this script any time you want to regenerate the CSV.
  Output is deterministic: same seed produces the same file.
"""

# === DECLARE IMPORTS ===

import csv
from datetime import datetime, timedelta
from pathlib import Path
import random
from typing import Final
import uuid

# === DECLARE CONSTANTS ===

SEED: Final[int] = 42

ROOT_DIR: Final[Path] = Path.cwd()
DATA_DIR: Final[Path] = ROOT_DIR / "data"
OUTPUT_CSV: Final[Path] = DATA_DIR / "sales.csv"

FIELDNAMES: Final[list[str]] = [
    "order_id",
    "datetime",
    "region_id",
    "currency_code",
    "product_id",
    "unit_price",
    "quantity",
    "is_online",
    "customer_id",
    "is_new_customer",
    "device_type",
    "payment_method",
    "referral_source",
    "discount_code",
    "customer_note",
]

# Products: (product_id, unit_price)
PRODUCTS: Final[list[tuple[str, float]]] = [
    ("PY-INTRO-001", 29.99),
    ("PY-DATA-002", 49.99),
    ("PY-VIZ-003", 39.99),
    ("PY-SQL-004", 44.99),
    ("PY-STREAM-005", 59.99),
    ("PY-NLP-006", 54.99),
]

# Regions: (region_id, currency_code)
REGIONS: Final[list[tuple[str, str]]] = [
    ("US-MO", "USD"),
    ("US-CA", "USD"),
    ("US-TX", "USD"),
    ("CA-ON", "CAD"),
    ("CA-QC", "CAD"),
    ("MX-CMX", "MXN"),
]

CUSTOMER_NOTES_POSITIVE: Final[list[str]] = [
    "Great course!",
    "Just what I needed",
    "Highly recommend",
    "Very helpful",
    "Clear explanations",
    "Worth every penny",
    "Already applying this at work",
    "Excellent content",
    "Love the examples",
]
CUSTOMER_NOTES_PROMO: Final[list[str]] = [
    "Love the discount!",
    "Great deal!",
    "Sharing with friends",
    "Bought two courses with this deal",
    "Finally pulled the trigger at this price",
    "Gifting this to my team",
]
CUSTOMER_NOTES_NEGATIVE: Final[list[str]] = [
    "Expected more content",
    "Good but could go deeper",
    "Slower than I expected",
]
CUSTOMER_NOTES_NEUTRAL: Final[list[str]] = [
    "",
    "",
    "",
    "",
    "",
    "Gift for my team",
    "For my study group",
    "Learning at my own pace",
    "Recommended by a colleague",
]


# === DEFINE HELPER FUNCTIONS ===


def weighted_pick(options: list, weights: list) -> object:
    """Pick one item from options using the given weights."""
    return random.choices(options, weights=weights, k=1)[0]


def make_customer_id() -> str:
    """Generate an anonymous customer ID."""
    return f"CUST-{random.randint(1000, 9999)}"


def make_order(
    dt: datetime,
    *,
    is_promo: bool = False,
    is_post_promo: bool = False,
    stream_boost: float = 1.0,
) -> dict[str, str | int | float]:
    """Generate a single sale record for the given datetime.

    Arguments:
        dt: The datetime of the order.
        is_promo: True during the Day 2 promotion window.
        is_post_promo: True during the Day 3 tail-off window.
        stream_boost: Multiplier for PY-STREAM-005 selection weight.

    Returns:
        A dictionary representing one sale record.
    """
    # Product selection: PY-STREAM-005 weight grows with stream_boost
    product_weights = [3, 2, 2, 2, int(3 * stream_boost), 2]
    product_id, unit_price = weighted_pick(PRODUCTS, product_weights)

    # Region selection: US regions slightly favored
    region_weights = [3, 3, 2, 2, 1, 1]
    region_id, currency_code = weighted_pick(REGIONS, region_weights)

    # During promo: more mobile, more new customers, more social/email referrals
    if is_promo:
        device_weights = [0.50, 0.30, 0.20]  # mobile, desktop, tablet
        new_customer_prob = 0.60
        referral_weights = [
            0.15,
            0.20,
            0.30,
            0.35,
        ]  # organic, paid_search, email, social
        discount_code = weighted_pick(["SPRING25", ""], [0.85, 0.15])
        note_pool = (
            CUSTOMER_NOTES_PROMO * 4 + CUSTOMER_NOTES_POSITIVE + CUSTOMER_NOTES_NEUTRAL
        )
    elif is_post_promo:
        device_weights = [0.38, 0.45, 0.17]
        new_customer_prob = 0.25
        referral_weights = [0.30, 0.25, 0.30, 0.15]
        discount_code = ""
        note_pool = CUSTOMER_NOTES_POSITIVE * 2 + CUSTOMER_NOTES_NEUTRAL
    else:
        device_weights = [0.33, 0.52, 0.15]
        new_customer_prob = 0.15
        referral_weights = [0.40, 0.30, 0.20, 0.10]
        discount_code = ""
        note_pool = (
            CUSTOMER_NOTES_POSITIVE
            + CUSTOMER_NOTES_NEGATIVE
            + CUSTOMER_NOTES_NEUTRAL * 2
        )

    device_type = weighted_pick(["mobile", "desktop", "tablet"], device_weights)
    is_new_customer = random.random() < new_customer_prob
    referral_source = weighted_pick(
        ["organic", "paid_search", "email", "social"], referral_weights
    )
    customer_note = random.choice(note_pool)

    # Apple Pay skews toward mobile + USD
    if device_type == "mobile" and currency_code == "USD":
        payment_weights = [0.30, 0.20, 0.45, 0.05]
    else:
        payment_weights = [0.55, 0.30, 0.10, 0.05]
    payment_method = weighted_pick(
        ["credit_card", "paypal", "apple_pay", "gift_card"], payment_weights
    )

    # Quantity: mostly 1, occasionally a team purchase
    quantity = weighted_pick([1, 2, 3, 4, 5], [0.60, 0.20, 0.10, 0.05, 0.05])

    is_online = random.random() < 0.92

    return {
        "order_id": str(uuid.uuid4()),
        "datetime": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "region_id": region_id,
        "currency_code": currency_code,
        "product_id": product_id,
        "unit_price": unit_price,
        "quantity": quantity,
        "is_online": str(is_online).lower(),
        "customer_id": make_customer_id(),
        "is_new_customer": str(is_new_customer).lower(),
        "device_type": device_type,
        "payment_method": payment_method,
        "referral_source": referral_source,
        "discount_code": discount_code,
        "customer_note": customer_note,
    }


def generate_orders() -> list[dict]:
    """Generate all orders according to the 3-day story.

    Segments: (start_hour_offset, end_hour_offset, count, is_promo, is_post_promo, stream_boost)

    Hours are offsets from Monday 2026-05-04 00:00:00.
    Day 1 = hours 8-21, Day 2 = hours 32-44, Day 3 = hours 56-68.

    Returns:
        A list of order dicts sorted by datetime.
    """
    base = datetime(2026, 5, 4, 0, 0, 0)  # Monday midnight

    segments = [
        # Day 1 Monday: normal sales day
        # (start_h, end_h, count, is_promo, is_post_promo, stream_boost)
        (8, 11, 18, False, False, 1.0),  # morning slow
        (11, 14, 28, False, False, 1.0),  # lunch rush
        (14, 17, 18, False, False, 1.0),  # afternoon
        (18, 21, 16, False, False, 1.0),  # evening
        # Day 2 Tuesday: SPRING25 promotion launches at 11am
        (32, 35, 8, False, False, 1.3),  # morning before promo
        (35, 40, 45, True, False, 1.5),  # promo spike: 11am-4pm
        (40, 44, 18, True, False, 1.4),  # promo tail: 4pm-8pm
        # Day 3 Wednesday: post-promo tail-off
        (56, 60, 12, False, True, 1.6),  # morning
        (60, 65, 10, False, True, 1.6),  # afternoon
        (65, 68, 5, False, True, 1.6),  # evening
    ]

    orders = []
    for start_h, end_h, count, is_promo, is_post_promo, stream_boost in segments:
        span_minutes = (end_h - start_h) * 60
        for _ in range(count):
            offset_minutes = random.randint(0, span_minutes)
            dt = base + timedelta(hours=start_h, minutes=offset_minutes)
            orders.append(
                make_order(
                    dt,
                    is_promo=is_promo,
                    is_post_promo=is_post_promo,
                    stream_boost=stream_boost,
                )
            )

    orders.sort(key=lambda r: r["datetime"])
    return orders


# === DEFINE THE MAIN FUNCTION ===


def main() -> None:
    """Generate the sales CSV and report the result."""
    random.seed(SEED)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    orders = generate_orders()

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(orders)

    print(f"Generated {len(orders)} orders. See:")
    print(f"{OUTPUT_CSV}")
    print()

    # Quick summary so you can verify the story is present
    promo_count = sum(1 for o in orders if o["discount_code"] == "SPRING25")
    new_cust_count = sum(1 for o in orders if o["is_new_customer"] == "true")
    stream_count = sum(1 for o in orders if o["product_id"] == "PY-STREAM-005")
    mobile_count = sum(1 for o in orders if o["device_type"] == "mobile")

    print(f"  Total orders:          {len(orders)}")
    print(f"  SPRING25 promo orders: {promo_count}")
    print(f"  New customers:         {new_cust_count}")
    print(f"  PY-STREAM-005 orders:  {stream_count}")
    print(f"  Mobile orders:         {mobile_count}")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    main()
