"""
Create sample CSV files for the agent demo.
This script generates multiple CSV files to test the agent's file discovery capabilities.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# 1. Sales Data (the main file the agent needs to find)
def generate_sales_data():
    """Generate synthetic sales transaction data with day-of-week patterns."""
    regions = ['North', 'South', 'East', 'West']
    channels = ['Online', 'Retail', 'Wholesale']
    start_date = datetime(2024, 1, 1)
    days = 120
    
    # Day of week effects (Monday=0, Sunday=6)
    dow_effects = {
        0: 0.88,  # Monday: -12%
        1: 1.00,  # Tuesday: baseline
        2: 1.02,  # Wednesday
        3: 1.05,  # Thursday
        4: 1.15,  # Friday: +15%
        5: 0.95,  # Saturday
        6: 0.92   # Sunday
    }
    
    transactions = []
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        dow = current_date.weekday()
        dow_multiplier = dow_effects[dow]
        
        # Number of transactions varies by day
        base_txns = np.random.poisson(50) + 20
        
        for _ in range(base_txns):
            timestamp = current_date + timedelta(
                hours=np.random.randint(0, 24),
                minutes=np.random.randint(0, 60)
            )
            
            region = np.random.choice(regions)
            channel = np.random.choice(channels)
            
            # Base amount with day-of-week effect
            base_amount = np.random.exponential(100) + 50
            amount = base_amount * dow_multiplier
            
            # Add some anomalies
            if day_offset == 45:  # Spike on day 45
                amount *= 2.5
            elif day_offset == 78:  # Slump on day 78
                amount *= 0.3
            elif day_offset == 100 and region == 'North':  # Regional surge
                amount *= 3.0
            
            transactions.append({
                'timestamp': timestamp.isoformat(),
                'amount': round(amount, 2),
                'region': region,
                'channel': channel
            })
    
    df = pd.DataFrame(transactions)
    return df.sort_values('timestamp').reset_index(drop=True)

# 2. HR Data (decoy file)
def generate_hr_data():
    """Generate synthetic HR employee data."""
    departments = ['Sales', 'Engineering', 'Marketing', 'Operations', 'Finance']
    locations = ['New York', 'San Francisco', 'London', 'Tokyo', 'Sydney']
    
    employees = []
    for i in range(500):
        employees.append({
            'employee_id': f'EMP{i:04d}',
            'department': np.random.choice(departments),
            'location': np.random.choice(locations),
            'salary': round(np.random.normal(75000, 20000), -3),
            'performance_score': round(np.random.uniform(1, 5), 1),
            'hire_date': (datetime.now() - timedelta(days=np.random.randint(30, 3650))).date().isoformat()
        })
    
    return pd.DataFrame(employees)

# 3. Leads Data (decoy file)
def generate_leads_data():
    """Generate synthetic sales leads data."""
    sources = ['Web', 'Email', 'Social', 'Referral', 'Event']
    statuses = ['New', 'Contacted', 'Qualified', 'Negotiation', 'Closed Won', 'Closed Lost']
    
    leads = []
    for i in range(1000):
        created = datetime.now() - timedelta(days=np.random.randint(0, 90))
        leads.append({
            'lead_id': f'LEAD{i:05d}',
            'source': np.random.choice(sources),
            'status': np.random.choice(statuses),
            'value': round(np.random.exponential(5000) + 1000, -2),
            'created_date': created.date().isoformat(),
            'last_contact': (created + timedelta(days=np.random.randint(0, 30))).date().isoformat()
        })
    
    return pd.DataFrame(leads)

# Generate and save all files
print("📊 Generating sample data files...")

# Sales data (the target file)
sales_df = generate_sales_data()
sales_df.to_csv('data/sales.csv', index=False)
print(f"✅ Created data/sales.csv - {len(sales_df)} transactions")

# HR data (decoy)
hr_df = generate_hr_data()
hr_df.to_csv('data/hr.csv', index=False)
print(f"✅ Created data/hr.csv - {len(hr_df)} employees")

# Leads data (decoy)
leads_df = generate_leads_data()
leads_df.to_csv('data/leads.csv', index=False)
print(f"✅ Created data/leads.csv - {len(leads_df)} leads")

print("\n📁 Files in data folder:")
import os
for file in os.listdir('data'):
    if file.endswith('.csv'):
        size = os.path.getsize(f'data/{file}') / 1024
        print(f"   - {file}: {size:.1f} KB")