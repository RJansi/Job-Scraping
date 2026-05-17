# Quick Start Guide - Naukri.com Job Scraper

## ⚠️ IMPORTANT: Naukri.com Anti-Scraping Protection

**Naukri.com has strong anti-scraping measures** (JavaScript rendering, CloudFlare, user-agent detection). Automated scraping has limited success.

### 🎯 RECOMMENDED SOLUTIONS:

## ✅ Solution 1: Browser Extension (FASTEST - 5 minutes)

1. Install **Table Capture** extension: https://chrome.google.com/webstore
2. Go to https://www.naukri.com/search
3. Search for jobs (Data Scientist, Tableau Developer, Python Developer, 11+ years, Bangalore/Chennai)
4. Right-click job list → "Capture table to CSV"
5. Save as `jobs_imported.csv`
6. Run: `python job_data_helper.py`
7. Select option 2 to import and analyze

## ✅ Solution 2: Manual Entry with Helper Tool

```bash
python job_data_helper.py
```

Then:
- Select option 1 to create template
- Edit the CSV file with jobs found on Naukri.com
- Select option 2 to import

## ✅ Solution 3: Automated Selenium Scraper (LIMITED SUCCESS)

```bash
python run.py
```

Select option 2 (Optimized Scraper) - may work but success varies due to anti-scraping measures.

## ✅ Solution 4: Manual Copy-Paste

1. Visit https://www.naukri.com/search
2. Search for jobs manually
3. Take screenshots or copy data
4. Use `job_data_helper.py` to organize data
5. Run analyzer

---

## 📋 What to Search For

**Search Parameters:**
- Keyword: Data Scientist / Tableau Developer / Python Developer
- Location: Bangalore / Chennai
- Experience: 11+ years
- Filter by: Google, Amazon, Meta, Apple, Netflix (if available)

---

## 📊 After Getting Job Data

### Process with Helper:
```bash
python job_data_helper.py
```
- Import CSV files
- Merge multiple searches
- Organize and clean data

### Analyze Results:
```bash
python data_analyzer.py
```
- Get statistics by company/location
- Generate reports
- Filter by criteria

---

## 🎯 Complete Workflow (10 minutes)

1. **Find jobs** (2-3 min):
   - Use browser extension to capture Naukri search results
   - OR manually search and copy data

2. **Import data** (1-2 min):
   ```bash
   python job_data_helper.py
   ```
   - Option 1: Create template
   - Option 2: Import exported CSV

3. **Analyze results** (1-2 min):
   ```bash
   python data_analyzer.py
   ```
   - View statistics
   - Get company breakdown
   - Export filtered results

4. **Review in Excel** (1-2 min):
   - Open generated CSV files
   - Sort, filter, apply formulas

---

## 📁 Files You'll Use

- `job_data_helper.py` - Manual entry & import tool ⭐ START HERE
- `data_analyzer.py` - Analysis & reporting
- `run.py` - Automated scraper (optional, limited success)
- `SOLUTIONS.md` - Detailed solution options

---

## 🚀 TL;DR - Do This Now

```bash
# Step 1: Open Naukri.com and manually search
https://www.naukri.com/search

# Step 2: Install browser extension to export
# OR use manual entry tool

# Step 3: Run helper to organize data
python job_data_helper.py

# Step 4: Analyze results
python data_analyzer.py
```

---

## 📞 Troubleshooting

**"Automated scraper not finding jobs"**
- This is expected due to anti-scraping measures
- Use browser extension method instead
- See SOLUTIONS.md for alternatives

**"How do I export from Naukri?"**
- Use Table Capture extension
- OR manually copy/paste into template
- See job_data_helper.py for easy import

**"Can I automate this completely?"**
- Partially - see SOLUTIONS.md
- Paid scraping services available
- Puppeteer (Node.js) alternative available

---

**Start with `python job_data_helper.py` - it's the easiest! 🎯**

