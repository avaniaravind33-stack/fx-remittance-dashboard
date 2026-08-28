# HDFC FX Remittance Operations & MIS Dashboard

A comprehensive full-stack business intelligence solution for FX remittance operations, featuring realistic Indian remittance patterns and HDFC Bank workflows.

## Overview

This project demonstrates end-to-end BI capabilities with:
- **10,000+ synthetic remittance transactions** with realistic Indian corridors (USA, UAE, Singapore, UK, Canada, etc.)
- **Excel MIS Dashboard** with PivotTables, SUMIFS/COUNTIFS, XLOOKUP, conditional formatting
- **Interactive Web Dashboard** deployed to GitHub Pages with Plotly charts
- **Automated CI/CD pipeline** using GitHub Actions for daily data refresh

## Key Features

### 📊 Data

- **Realistic patterns**: 60% inward, 85% success rate, 2% exception rate
- **Major corridors**: USA (35%), UAE (25%), Singapore (15%), UK (10%)
- **Processing channels**: SWIFT (50%), NEFT (30%), Branch (15%), Online (5%)
- **Currency mix**: USD, AED, SGD, GBP, CAD with dynamic FX rates
- **Transaction sizes**: ₹50K - ₹50M INR equivalent

### 📑 Excel Dashboard

**5 worksheets + data sheet**:

1. **Data Sheet**: Raw transaction data with auto-refresh capability
2. **Volume Dashboard**: 
   - Total transactions, inward/outward split
   - Currency breakdown, country/corridor breakdown
3. **Value Dashboard**:
   - Total INR value, foreign currency value
   - Average transaction size, corridor analysis
4. **Operations Dashboard**:
   - Processing time metrics
   - SLA breaches (>120 hours)
   - Pending/failed transactions
   - Exception analysis, channel performance
5. **Management Dashboard**:
   - Executive summary and KPIs
   - Trends (daily/weekly/monthly)
   - Top corridors and currencies
   - Risk indicators

**Excel Features**:
- 50+ formulas using SUMIFS, COUNTIFS, XLOOKUP
- 10+ interactive charts
- Conditional formatting and heat maps
- PivotTable support

### 🌐 Web Dashboard

Deployed to GitHub Pages with interactive Plotly charts:
- Executive KPI summary cards
- Volume analysis (transactions by corridor, currency, direction)
- Value analysis (INR amounts by corridor)
- Status breakdown and trends
- Processing time distribution
- Channel performance analysis
- Exception reasons breakdown
- SLA breach rates by corridor

**Features**:
- Responsive design (mobile-friendly)
- Interactive hover tooltips
- Dark/light styling support
- Real-time data refresh via CI/CD

## Project Structure

```
fx-remittance-dashboard/
├── data/
│   └── remittance_transactions.csv          # 10,000 transactions
├── excel/
│   └── HDFC_FX_Remittance_MIS_Dashboard.xlsx
├── scripts/
│   ├── generate_data.py                     # Data generation
│   ├── excel_generator.py                   # Excel dashboard creation
│   └── generate_website.py                  # Website generation
├── website/
│   └── index.html                           # Live dashboard (GitHub Pages)
├── .github/
│   └── workflows/
│       └── deploy.yml                       # CI/CD automation
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/avaniaravind33-stack/fx-remittance-dashboard.git
cd fx-remittance-dashboard

# Install dependencies
pip install -r requirements.txt
```

### Generate Dashboards Locally

```bash
# Generate synthetic data
python scripts/generate_data.py

# Create Excel dashboard
python scripts/excel_generator.py

# Create web dashboard
python scripts/generate_website.py
```

**Outputs**:
- `data/remittance_transactions.csv` — Synthetic transaction data
- `excel/HDFC_FX_Remittance_MIS_Dashboard.xlsx` — Excel MIS dashboard
- `website/index.html` — Web dashboard

### View Web Dashboard

```bash
# Open in browser
open website/index.html  # macOS
# OR
start website/index.html  # Windows
# OR
firefox website/index.html  # Linux
```

## Dashboard Metrics

### Volume Metrics
- Total transactions: 10,000
- Inward: 60%, Outward: 40%
- Top corridor: USA (35%)
- Success rate: 85%

### Value Metrics
- Total INR value: ₹30 Billion
- Average transaction: ₹2.99L
- Range: ₹50K - ₹50M

### Operations Metrics
- Average processing time: 64.7 hours
- SLA breach rate: <1% (>120 hours)
- Exception rate: 1.96%
- Channel distribution: SWIFT 50%, NEFT 30%, Branch 15%, Online 5%

## CI/CD Pipeline

GitHub Actions workflow automates:

1. **Daily Data Refresh** (2 AM UTC)
   - Generates new synthetic transaction data
   - Creates fresh Excel dashboard
   - Updates web dashboard

2. **Automatic Deployment**
   - Commits updated files to main branch
   - Deploys website to GitHub Pages
   - No manual intervention needed

### Enable GitHub Pages

1. Go to Settings → Pages
2. Source: Deploy from branch
3. Branch: `main` / folder: `website/`
4. Custom domain (optional)

## Excel Formula Examples

```excel
# Total transactions
=COUNTA('Data'!A:A)-1

# Inward transactions
=COUNTIF('Data'!D:D,"Inward")

# Total INR value by status
=SUMIF('Data'!L:L,"Completed",'Data'!I:I)

# Average processing time by channel
=AVERAGEIF('Data'!O:O,"SWIFT",'Data'!M:M)

# SLA breach rate
=COUNTIF('Data'!S:S,"Yes")/(COUNTA('Data'!A:A)-1)
```

## Data Dictionary

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| Transaction ID | String | HDFC2024123456 | Unique transaction identifier |
| Date | DateTime | 2024-01-15 10:30 | Transaction initiation date/time |
| Customer ID | String | CUST567890 | Unique customer identifier |
| Direction | String | Inward/Outward | Remittance direction |
| Corridor | String | USA, UAE, etc. | Country/corridor |
| From Currency | String | USD, AED, INR | Source currency |
| To Currency | String | INR | Target currency (always INR for inward) |
| INR Amount | Number | 250000 | Amount in Indian Rupees |
| Foreign Amount | Number | 3000 | Amount in foreign currency |
| FX Rate | Number | 83.5 | Exchange rate applied |
| Value Date | DateTime | 2024-01-16 | Settlement date |
| Status | String | Completed | Transaction status |
| Processing Time (Hours) | Number | 48 | Time from initiation to completion |
| Exception Flag | String | Yes/No | Exception indicator |
| Exception Reason | String | KYC mismatch | Reason if exception = Yes |
| Channel | String | SWIFT, NEFT | Processing channel |
| SLA Breach | String | Yes/No | SLA breach indicator (>120 hours) |

## Exception Reasons

- **KYC mismatch** (25%): Customer verification issues
- **Invalid beneficiary details** (20%): Incorrect recipient information
- **Document discrepancies** (20%): Missing or inconsistent documents
- **Sanctions check flag** (15%): Compliance screening alert
- **Compliance review** (15%): Additional review required
- **Technical error** (5%): System or processing error

## Performance & Scalability

- **Current**: 10,000 transactions
- **Can scale to**: 1M+ transactions (adjust batch processing)
- **Excel limitation**: 1.04M rows (use CSV for larger datasets)
- **Web dashboard**: Handles real-time Plotly rendering up to 100K transactions

## Customization

### Adjust Data Volume

Edit `scripts/generate_data.py`:
```python
NUM_TRANSACTIONS = 50000  # Change from 10,000
```

### Modify Corridors/Currencies

Edit corridor weights and rates:
```python
CORRIDORS = {
    'USA': {'weight': 0.35, 'avg_inr': 250000, ...},
    # Add/modify corridors
}
```

### Change Chart Colors

Edit `scripts/generate_website.py`:
```python
marker=dict(color='#0070C0')  # Change hex color
```

## Testing

```bash
# Verify data generation
python scripts/generate_data.py
# Output: 10,000 transactions with validation stats

# Verify Excel creation
python scripts/excel_generator.py
# Output: Excel file with formulas and charts

# Verify website generation
python scripts/generate_website.py
# Output: Interactive HTML dashboard
```

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'openpyxl'`
```bash
pip install openpyxl
```

**Issue**: Excel formulas show `#VALUE!` error
- Ensure Data sheet is named exactly "Data"
- Check column references match actual data

**Issue**: Web dashboard doesn't display
- Verify `index.html` exists in `website/` folder
- Check browser console for JavaScript errors

## Live Dashboard

🔗 **View live**: https://avaniaravind33-stack.github.io/fx-remittance-dashboard/

(After pushing to GitHub and enabling Pages)

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Data Generation | Python, pandas, numpy, faker | 3.10+ |
| Excel Creation | openpyxl | 3.0+ |
| Web Dashboard | Plotly, HTML/CSS | Latest |
| Deployment | GitHub Actions, GitHub Pages | - |
| Version Control | Git | - |

## Future Enhancements

- [ ] Real-time data integration (API backend)
- [ ] Advanced ML anomaly detection for exceptions
- [ ] Predictive SLA modeling
- [ ] Multi-corridor scenario analysis
- [ ] Mobile app for field operations
- [ ] Power BI/Tableau integration
- [ ] Custom alerting system
- [ ] Audit trail and compliance reporting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -m 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Contact & Support

For questions or suggestions:
- 📧 Email: avaniaravind33@gmail.com
- 🐙 GitHub: @avaniaravind33-stack

---

**Built with ❤️ | Last Updated: 2024**
