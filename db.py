# db.py
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# 1. SETUP CONNECTION
# Make sure your .env has: DATABASE_URL="postgresql://user:pass@localhost:5432/argos_db"
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_real_data():
    """
    Fetches actual transactions from PostgreSQL and returns a Pandas DataFrame.
    """
    # Matches your Prisma Schema exactly
    query = """
    SELECT 
        id, 
        date, 
        merchant, 
        category, 
        CAST(amount AS FLOAT) as amount, -- CRITICAL: Convert Decimal to Float for AI/Plotting
        currency,
        "bankName",  -- e.g. HDFC, SBI
        source       -- e.g. GMAIL, MANUAL, WHATSAPP
    FROM "Transaction"
    ORDER BY date DESC
    LIMIT 1000;
    """
    
    try:
        # Load SQL directly into Pandas
        df = pd.read_sql(query, engine)
        
        # Ensure dates are actual datetime objects
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = get_real_data()
    print(f"✅ Loaded {len(df)} rows from Real DB")
    if not df.empty:
        print(df.head())