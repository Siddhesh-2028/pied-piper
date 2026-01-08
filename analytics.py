# analytics.py
import pandas as pd
from mock_db import get_all_data

def get_trends():
    df = get_all_data()
    
    # 1. Monthly Trend
    # Convert date column to datetime objects
    df['dt'] = pd.to_datetime(df['date'])
    # Group by Month Name (Jan, Feb)
    monthly = df.groupby(df['dt'].dt.strftime('%B'))['amount'].sum().reset_index()
    monthly.columns = ['month', 'total']
    
    # 2. Category Split
    category = df.groupby('category')['amount'].sum().reset_index()
    category.columns = ['name', 'value'] # Format for Recharts
    
    return {
        "monthly_trend": monthly.to_dict(orient="records"),
        "category_split": category.to_dict(orient="records")
    }