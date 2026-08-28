# GitHub Deployment Guide

## Quick Setup (5 minutes)

### 1. Add GitHub Remote
```bash
git remote add origin https://github.com/avaniaravind33-stack/fx-remittance-dashboard.git
git branch -M main
git push -u origin main
```

### 2. Enable GitHub Pages
1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under "Source", select:
   - Branch: `main`
   - Folder: `/website`
4. Click **Save**

### 3. View Live Dashboard
Wait 1-2 minutes for deployment, then visit:
```
https://avaniaravind33-stack.github.io/fx-remittance-dashboard/
```

## What Happens Automatically

### On Every Push
- ✅ GitHub Actions workflow triggers
- ✅ Regenerates synthetic data
- ✅ Creates fresh Excel dashboard
- ✅ Builds web dashboard
- ✅ Auto-commits changes
- ✅ Deploys to GitHub Pages

### Daily at 2 AM UTC
- ✅ Automatic data refresh
- ✅ New dashboards generated
- ✅ Website updated live
- ✅ All changes committed

## File Locations

| File | Purpose | Size |
|------|---------|------|
| `data/remittance_transactions.csv` | Transaction data | 1.2 MB |
| `excel/HDFC_FX_Remittance_MIS_Dashboard.xlsx` | Excel dashboard | 964 KB |
| `website/index.html` | Web dashboard | 7.2 KB |
| `.github/workflows/deploy.yml` | CI/CD pipeline | - |

## Troubleshooting

**Website not updating?**
- Check Actions tab for workflow errors
- Verify Pages source is set to `/website` folder
- Wait 2-3 minutes after push

**Excel formulas broken?**
- Regenerate locally: `python scripts/excel_generator.py`
- Check Data sheet exists
- Commit and push

**Data seems outdated?**
- Manual refresh: `python scripts/generate_data.py`
- Or wait for 2 AM UTC daily run
- Commit and push changes

## Local Testing

```bash
# Generate all dashboards
python scripts/generate_data.py
python scripts/excel_generator.py
python scripts/generate_website.py

# View web dashboard
open website/index.html
```

## Need Help?

See `README.md` for detailed documentation and customization options.
