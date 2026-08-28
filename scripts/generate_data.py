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

def generate_reconciliation_data(df):
    """Generate reconciliation records for transactions"""
    print("\nGenerating reconciliation records...")

    reconciliation_records = []

    # 85% matched, 15% have issues
    for idx, tx in df.iterrows():
        recon_id = f"RECON{idx+1:06d}"
        tx_id = tx['Transaction ID']

        # Determine reconciliation status
        rand = random.random()

        if rand < 0.85:  # 85% matched
            status = 'Matched'
            issue_type = 'None'
            difference_amount = 0
            difference_percentage = 0
        elif rand < 0.90:  # 5% amount mismatch
            status = 'Unmatched'
            issue_type = 'Amount Mismatch'
            difference_amount = random.randint(-5000, 5000)
            difference_percentage = (difference_amount / tx['INR Amount'] * 100) if tx['INR Amount'] > 0 else 0
        elif rand < 0.94:  # 4% missing settlement
            status = 'Unmatched'
            issue_type = 'Missing Settlement'
            difference_amount = tx['INR Amount']
            difference_percentage = 100
        elif rand < 0.97:  # 3% duplicate
            status = 'Duplicate'
            issue_type = 'Duplicate Transaction'
            difference_amount = 0
            difference_percentage = 0
        else:  # 3% FX rate discrepancy
            status = 'Unmatched'
            issue_type = 'FX Rate Discrepancy'
            difference_amount = 0
            difference_percentage = round(random.uniform(-2, 2), 2)

        # Resolution time based on status
        if status == 'Matched':
            days_to_resolve = 0
            resolution_date = tx['Date']
        else:
            days_to_resolve = random.randint(1, 15)
            resolution_date = (pd.to_datetime(tx['Date']) + timedelta(days=days_to_resolve)).strftime('%Y-%m-%d')

        reconciliation_records.append({
            'Recon ID': recon_id,
            'Transaction ID': tx_id,
            'Recon Date': tx['Date'],
            'Status': status,
            'Issue Type': issue_type,
            'Amount Difference (INR)': difference_amount,
            'FX Rate Variance (%)': difference_percentage,
            'Days to Resolve': days_to_resolve,
            'Resolution Date': resolution_date,
        })

    recon_df = pd.DataFrame(reconciliation_records)
    print(f"\nReconciliation Status:")
    print(recon_df['Status'].value_counts())
    print(f"\nIssue Types:")
    print(recon_df[recon_df['Status'] != 'Matched']['Issue Type'].value_counts())

    return recon_df

def generate_query_data(df):
    """Generate customer query management records"""
    print("\nGenerating query records...")

    query_records = []
    query_types = ['Payment Delay', 'FX Rate Query', 'Missing Credit', 'Amount Discrepancy',
                   'Duplicate Charge', 'Settlement Inquiry', 'Document Request', 'Compliance Check']
    statuses = ['Resolved', 'Closed', 'Escalated', 'Pending', 'In Progress']

    # Generate ~200 queries (2% of transactions)
    num_queries = int(len(df) * 0.02)

    for i in range(num_queries):
        query_id = f"Q{i+1:05d}"
        query_type = random.choice(query_types)

        # Link to a random transaction
        linked_tx = df.sample(1).iloc[0]

        # Query creation date (random within data range)
        query_date = (pd.to_datetime(linked_tx['Date']) + timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d')

        # Priority based on type
        if query_type in ['Missing Credit', 'Payment Delay']:
            priority = random.choice(['High', 'High', 'Medium'])  # Weighted to High
        elif query_type in ['Compliance Check', 'Duplicate Charge']:
            priority = random.choice(['High', 'Medium', 'Medium'])
        else:
            priority = random.choice(['Medium', 'Low', 'Low'])

        # Status distribution
        status = random.choices(
            ['Resolved', 'Closed', 'In Progress', 'Escalated', 'Pending'],
            weights=[0.50, 0.25, 0.15, 0.07, 0.03]
        )[0]

        # Resolution time
        if status in ['Resolved', 'Closed']:
            resolution_days = random.randint(1, 10)
        elif status == 'In Progress':
            resolution_days = random.randint(1, 3)
        elif status == 'Escalated':
            resolution_days = random.randint(3, 7)
        else:  # Pending
            resolution_days = random.randint(1, 2)

        resolution_date = (pd.to_datetime(query_date) + timedelta(days=resolution_days)).strftime('%Y-%m-%d')

        # Resolution notes
        resolution_notes = {
            'Payment Delay': 'Checked with bank, payment en route',
            'FX Rate Query': f'Current rate {linked_tx["FX Rate"]}, explained to customer',
            'Missing Credit': 'Amount credited to account after investigation',
            'Amount Discrepancy': 'Discrepancy resolved, documentation provided',
            'Duplicate Charge': 'Duplicate identified and refunded',
            'Settlement Inquiry': 'Settlement confirmed, documentation sent',
            'Document Request': 'Documents provided to customer',
            'Compliance Check': 'Verification completed, transaction approved'
        }

        query_records.append({
            'Query ID': query_id,
            'Query Type': query_type,
            'Transaction ID': linked_tx['Transaction ID'],
            'Query Date': query_date,
            'Priority': priority,
            'Status': status,
            'Resolution Date': resolution_date,
            'Days to Resolve': resolution_days,
            'Resolution Notes': resolution_notes[query_type],
        })

    query_df = pd.DataFrame(query_records)
    print(f"\nQuery Status Distribution:")
    print(query_df['Status'].value_counts())
    print(f"\nQuery Type Distribution:")
    print(query_df['Query Type'].value_counts())
    print(f"\nAverage Resolution Time: {query_df['Days to Resolve'].mean():.1f} days")

    return query_df

def main():
    # Generate data
    df = generate_dataset()

    # Validate
    validate_dataset(df)

    # Save to CSV
    output_path = 'data/remittance_transactions.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✓ Dataset saved to {output_path}")

    # Generate reconciliation data
    print("\n" + "="*50)
    print("GENERATING RECONCILIATION DATA")
    print("="*50)
    recon_df = generate_reconciliation_data(df)
    recon_path = 'data/reconciliation_records.csv'
    recon_df.to_csv(recon_path, index=False)
    print(f"✓ Reconciliation data saved to {recon_path}")

    # Generate query data
    print("\n" + "="*50)
    print("GENERATING QUERY MANAGEMENT DATA")
    print("="*50)
    query_df = generate_query_data(df)
    query_path = 'data/query_management.csv'
    query_df.to_csv(query_path, index=False)
    print(f"✓ Query data saved to {query_path}")

    return df, recon_df, query_df

if __name__ == '__main__':
    main()
