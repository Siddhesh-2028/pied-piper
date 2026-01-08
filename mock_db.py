# mock_db.py
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_static_data():
    """
    Generates a realistic DataFrame of 100 transactions
    spanning the last 3 months.
    """
    data = []
    
    # Configuration for realistic data
    merchants = {
        "Food": ["Swiggy", "Zomato", "Starbucks", "KFC", "Dominos"],
        "Transport": ["Uber", "Ola", "Rapido", "Shell Fuel", "IndiGo"],
        "Shopping": ["Amazon", "Flipkart", "Myntra", "Uniqlo"],
        "Bills": ["Jio Prepaid", "Bescom", "Netflix", "ACT Fibernet", "HDFC CC Bill"],
        "Entertainment": ["BookMyShow", "PVR", "Steam Games"]
    }
    
    start_date = datetime.now()
    
    for i in range(100):
        # 1. Pick a random category and merchant
        cat = random.choice(list(merchants.keys()))
        merch = random.choice(merchants[cat])
        
        # 2. Generate random amount (weighted logic)
        if cat == "Bills" or cat == "Shopping":
            amount = random.randint(500, 15000)
        elif cat == "Food":
            amount = random.randint(150, 1500)
        else:
            amount = random.randint(50, 2000)
            
        # 3. Generate date (Last 90 days)
        days_ago = random.randint(0, 90)
        txn_date = (start_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # 4. Append
        data.append({
            "id": f"txn_{i}",
            "date": txn_date,
            "merchant": merch,
            "category": cat,
            "amount": amount,
            "currency": "INR",
            "payment_method": random.choice(["UPI", "Credit Card", "Debit Card"])
        })
        
    # Create the DataFrame
    df = pd.DataFrame(data)
    
    # Ensure types are correct for PandasAI to read them
    df['amount'] = df['amount'].astype(float)
    df['date'] = pd.to_datetime(df['date'])
    
    return df

# Simple test to run this file directly
if __name__ == "__main__":
    df = generate_static_data()
    print(f"✅ Generated {len(df)} transactions.")
    print(df.head())