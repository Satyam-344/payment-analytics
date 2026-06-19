import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

NUM_USERS = 5000
NUM_TRANSACTIONS = 50000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

CATEGORIES = {
    "Food & Dining": 0.22,
    "Shopping": 0.18,
    "Transport": 0.15,
    "Recharge & Bills": 0.14,
    "Entertainment": 0.09,
    "Health": 0.07,
    "Travel": 0.08,
    "Education": 0.04,
    "Others": 0.03,
}

PAYMENT_METHODS = {
    "UPI": 0.55,
    "Debit Card": 0.18,
    "Credit Card": 0.15,
    "Wallet": 0.08,
    "Net Banking": 0.04,
}

CITIES = {
    "Mumbai": 0.18, "Delhi": 0.16, "Bangalore": 0.14,
    "Hyderabad": 0.10, "Chennai": 0.09, "Pune": 0.08,
    "Kolkata": 0.07, "Ahmedabad": 0.06, "Jaipur": 0.05,
    "Others": 0.07,
}

MERCHANTS = {
    "Food & Dining": ["Swiggy", "Zomato", "McDonald's", "Domino's", "KFC", "Local Restaurant"],
    "Shopping": ["Amazon", "Flipkart", "Meesho", "Myntra", "Nykaa", "Local Store"],
    "Transport": ["Ola", "Uber", "Rapido", "Metro", "IRCTC", "RedBus"],
    "Recharge & Bills": ["Airtel", "Jio", "BSNL", "Electricity Board", "Gas Agency"],
    "Entertainment": ["BookMyShow", "Netflix", "Hotstar", "Spotify", "PVR Cinemas"],
    "Health": ["Apollo Pharmacy", "Netmeds", "1mg", "Practo", "Local Clinic"],
    "Travel": ["MakeMyTrip", "Goibibo", "OYO", "Airbnb", "Airlines"],
    "Education": ["Coursera", "Udemy", "BYJU's", "Unacademy", "College Fee"],
    "Others": ["Amazon Pay", "PayTm Mall", "eBay", "Miscellaneous"],
}

AMOUNT_RANGES = {
    "Food & Dining": (50, 800),
    "Shopping": (100, 5000),
    "Transport": (20, 500),
    "Recharge & Bills": (100, 2000),
    "Entertainment": (50, 1500),
    "Health": (100, 3000),
    "Travel": (500, 15000),
    "Education": (500, 20000),
    "Others": (50, 2000),
}

AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS = ["Male", "Female", "Other"]

def weighted_choice(options_dict):
    keys = list(options_dict.keys())
    weights = list(options_dict.values())
    return np.random.choice(keys, p=weights)

def generate_hour():
    # Model realistic transaction hours — peak at lunch, evening
    hours = list(range(24))
    raw = [
        0.01, 0.01, 0.005, 0.005, 0.005, 0.01,  # 0-5 AM
        0.02, 0.04, 0.05, 0.05, 0.04, 0.06,     # 6-11 AM
        0.08, 0.07, 0.05, 0.05, 0.06, 0.07,     # 12-5 PM
        0.08, 0.09, 0.08, 0.06, 0.04, 0.02      # 6-11 PM
    ]
    total = sum(raw)
    weights = [w / total for w in raw]
    return np.random.choice(hours, p=weights)

def generate_transactions():
    users = []
    for i in range(NUM_USERS):
        users.append({
            "user_id": f"USR{i+1:05d}",
            "age_group": np.random.choice(AGE_GROUPS, p=[0.28, 0.35, 0.20, 0.11, 0.06]),
            "gender": np.random.choice(GENDERS, p=[0.58, 0.40, 0.02]),
            "city": weighted_choice(CITIES),
        })
    users_df = pd.DataFrame(users)

    records = []
    date_range = (END_DATE - START_DATE).days

    for i in range(NUM_TRANSACTIONS):
        user = users_df.sample(1).iloc[0]
        category = weighted_choice(CATEGORIES)
        payment_method = weighted_choice(PAYMENT_METHODS)
        merchant = random.choice(MERCHANTS[category])

        days_offset = np.random.randint(0, date_range)
        txn_date = START_DATE + timedelta(days=int(days_offset))
        txn_hour = generate_hour()

        low, high = AMOUNT_RANGES[category]
        amount = round(np.random.lognormal(
            mean=np.log((low + high) / 2),
            sigma=0.5
        ), 2)
        amount = max(low, min(high, amount))

        # 94% success rate overall; vary by method
        success_rates = {
            "UPI": 0.95, "Debit Card": 0.93,
            "Credit Card": 0.96, "Wallet": 0.97, "Net Banking": 0.91
        }
        status = "Success" if np.random.random() < success_rates[payment_method] else "Failed"

        records.append({
            "transaction_id": f"TXN{i+1:07d}",
            "user_id": user["user_id"],
            "age_group": user["age_group"],
            "gender": user["gender"],
            "city": user["city"],
            "date": txn_date.strftime("%Y-%m-%d"),
            "hour": txn_hour,
            "day_of_week": txn_date.strftime("%A"),
            "month": txn_date.strftime("%B"),
            "month_num": txn_date.month,
            "quarter": f"Q{(txn_date.month - 1) // 3 + 1}",
            "category": category,
            "merchant": merchant,
            "payment_method": payment_method,
            "amount": amount,
            "status": status,
        })

    df = pd.DataFrame(records)
    df.to_csv("transactions.csv", index=False)
    print(f"Generated {len(df)} transactions for {NUM_USERS} users.")
    print(df.head())
    return df

if __name__ == "__main__":
    generate_transactions()
