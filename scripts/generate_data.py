"""
FX Remittance Transaction Data Generator
Generates realistic Indian remittance transaction data with HDFC Bank patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker(['en_IN'])

# Configuration
NUM_TRANSACTIONS = 10000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

# Realistic Indian remittance patterns
CORRIDORS = {
    'USA': {'weight': 0.35, 'avg_inr': 250000, 'currency': 'USD', 'avg_fx': 83.5},
    'UAE': {'weight': 0.25, 'avg_inr': 180000, 'currency': 'AED', 'avg_fx': 22.7},
    'Singapore': {'weight': 0.15, 'avg_inr': 220000, 'currency': 'SGD', 'avg_fx': 62.0},
    'UK': {'weight': 0.10, 'avg_inr': 200000, 'currency': 'GBP', 'avg_fx': 105.0},
    'Canada': {'weight': 0.05, 'avg_inr': 210000, 'currency': 'CAD', 'avg_fx': 61.0},
    'Australia': {'weight': 0.05, 'avg_inr': 230000, 'currency': 'AUD', 'avg_fx': 55.0},
    'Malaysia': {'weight': 0.03, 'avg_inr': 150000, 'currency': 'MYR', 'avg_fx': 17.5},
    'Thailand': {'weight': 0.02, 'avg_inr': 120000, 'currency': 'THB', 'avg_fx': 2.3},
}

CHANNELS = ['SWIFT', 'NEFT', 'Branch', 'Online']
CHANNEL_WEIGHTS = [0.50, 0.30, 0.15, 0.05]

STATUS_DISTRIBUTION = {
    'Completed': 0.85,
    'Pending': 0.08,
    'On-hold': 0.02,
    'Failed': 0.05
}

EXCEPTION_REASONS = {
    'KYC mismatch': 0.25,
    'Invalid beneficiary details': 0.20,
    'Document discrepancies': 0.20,
    'Sanctions check flag': 0.15,
    'Compliance review': 0.15,
    'Technical error': 0.05,
}

def generate_transaction_date():
    """Generate random transaction date within range"""
    time_diff = END_DATE - START_DATE
    random_days = random.randint(0, time_diff.days)
    return START_DATE + timedelta(days=random_days, hours=random.randint(0, 23), minutes=random.randint(0, 59))

def generate_processing_time(status):
    """Generate realistic processing time based on status"""
    if status == 'Completed':
        # 1-5 business days = 24-120 hours
        return random.randint(24, 120)
    elif status == 'Pending':
        # Currently processing
        return random.randint(1, 48)
    elif status == 'Failed':
        # Quick failure
        return random.randint(1, 24)
    else:  # On-hold
        # Held for review
        return random.randint(24, 72)

def generate_fx_rate(base_rate):
    """Generate realistic FX rate with minor variance"""
    variance = random.uniform(-0.02, 0.02)  # +/- 2% variance
    return round(base_rate * (1 + variance), 2)

def generate_transaction():
    """Generate single realistic remittance transaction"""

    # Select corridor
    corridor = np.random.choice(
        list(CORRIDORS.keys()),
        p=[CORRIDORS[k]['weight'] for k in CORRIDORS.keys()]
    )
    corridor_info = CORRIDORS[corridor]

    # Transaction details
    tx_id = f"HDFC{datetime.now().year}{random.randint(100000, 999999)}"
    tx_date = generate_transaction_date()
    customer_id = f"CUST{random.randint(100000, 999999)}"

    # Direction: 60% inward, 40% outward
    direction = 'Inward' if random.random() < 0.60 else 'Outward'

    # Amount
    inr_amount = round(np.random.lognormal(
        mean=np.log(corridor_info['avg_inr']),
        sigma=0.8
    ), 0)
    inr_amount = max(50000, min(5000000, inr_amount))  # Clamp between 50K-5M

    # FX rate
    fx_rate = generate_fx_rate(corridor_info['avg_fx'])
    foreign_amount = round(inr_amount / fx_rate, 2)

    # Status
    status = np.random.choice(
        list(STATUS_DISTRIBUTION.keys()),
        p=list(STATUS_DISTRIBUTION.values())
    )

    # Processing time
    processing_time = generate_processing_time(status)

    # Exception flag (2% overall rate)
    has_exception = random.random() < 0.02
    if has_exception:
        exception_reason = np.random.choice(
            list(EXCEPTION_REASONS.keys()),
            p=list(EXCEPTION_REASONS.values())
        )
    else:
        exception_reason = 'None'

    # Channel
    channel = np.random.choice(CHANNELS, p=CHANNEL_WEIGHTS)

    # Value date (typically 1-2 business days after transaction)
    value_date = tx_date + timedelta(days=random.randint(1, 2))

    # SLA check (SLA is 120 hours = 5 days for completed)
    sla_breach = 'Yes' if (status == 'Completed' and processing_time > 120) else 'No'

    return {
        'Transaction ID': tx_id,
        'Date': tx_date.strftime('%Y-%m-%d'),
        'Time': tx_date.strftime('%H:%M:%S'),
        'Customer ID': customer_id,
        'Direction': direction,
        'Corridor': corridor,
        'From Currency': corridor_info['currency'] if direction == 'Inward' else 'INR',
        'To Currency': 'INR' if direction == 'Inward' else corridor_info['currency'],
        'INR Amount': inr_amount,
        'Foreign Amount': foreign_amount,
        'FX Rate': fx_rate,
        'Value Date': value_date.strftime('%Y-%m-%d'),
        'Status': status,
        'Processing Time (Hours)': processing_time,
        'Exception Flag': 'Yes' if has_exception else 'No',
        'Exception Reason': exception_reason,
        'Channel': channel,
        'SLA Breach': sla_breach,
    }

def generate_dataset(num_transactions=NUM_TRANSACTIONS):
    """Generate full dataset of transactions"""
    print(f"Generating {num_transactions} realistic remittance transactions...")

    transactions = []
    for i in range(num_transactions):
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1} transactions...")
        transactions.append(generate_transaction())

    df = pd.DataFrame(transactions)

    # Convert date columns to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df['Value Date'] = pd.to_datetime(df['Value Date'])

    # Sort by date
    df = df.sort_values('Date').reset_index(drop=True)

    return df

def validate_dataset(df):
    """Validate dataset distributions"""
    print("\n=== Dataset Validation ===")
    print(f"Total transactions: {len(df)}")
    print(f"\nDirection breakdown:")
    print(df['Direction'].value_counts(normalize=True))
    print(f"\nStatus breakdown:")
    print(df['Status'].value_counts(normalize=True))
    print(f"\nCorridor breakdown:")
    print(df['Corridor'].value_counts(normalize=True))
    print(f"\nChannel breakdown:")
    print(df['Channel'].value_counts(normalize=True))
    print(f"\nException rate: {(df['Exception Flag'] == 'Yes').sum() / len(df) * 100:.2f}%")
    print(f"SLA breach rate: {(df['SLA Breach'] == 'Yes').sum() / len(df) * 100:.2f}%")
    print(f"\nINR Amount stats:")
    print(df['INR Amount'].describe())
    print(f"\nProcessing time stats:")
    print(df['Processing Time (Hours)'].describe())

def main():
    # Generate data
    df = generate_dataset()

    # Validate
    validate_dataset(df)

    # Save to CSV
    output_path = 'data/remittance_transactions.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✓ Dataset saved to {output_path}")

    return df

if __name__ == '__main__':
    main()
