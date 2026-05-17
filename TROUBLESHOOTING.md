# 🔍 Naukri.com Scraper - Troubleshooting Guide

## Problem: Not Getting Any Job Listings

**Cause:** Naukri.com dynamically loads job listings using JavaScript. The basic HTTP scraper cannot access JavaScript-rendered content.

## ✅ Solution: Use Selenium Scraper

The Selenium scraper uses a real browser to load JavaScript, so it can see the actual job listings.

### Quick Fix - Run Selenium Scraper

**Option 1: Direct Command**
```bash
python naukri_selenium_scraper.py
```

**Option 2: Using Interactive Menu**
```bash
python run.py
```
Then select option **2** (Advanced Scraper - Selenium)

**Option 3: Quick debug**
```bash
python debug_scraper.py
```

---

## 📋 How It Works

### Basic Scraper (HTTP only)
```
Browser Request → HTML (without job data) → No results ❌
```

### Selenium Scraper (Real browser)
```
Selenium WebDriver → Chrome/Firefox → JavaScript renders → Job data ✅
```

---

## 🚀 Installation Requirements

All packages are already installed, but verify with:
```bash
pip list | grep -E "selenium|beautifulsoup4|requests"
```

Should show:
- ✓ selenium >= 4.15.0
- ✓ beautifulsoup4 >= 4.12.0
- ✓ requests >= 2.31.0

---

## 🔧 Advanced Troubleshooting

### If Selenium scraper shows "ChromeDriver not found"

1. **Download ChromeDriver:**
   - Go to: https://chromedriver.chromium.org/
   - Download version matching your Chrome browser
   - Add to system PATH or place in project folder

2. **Check Chrome version:**
   ```bash
   chrome --version
   ```

3. **Verify Selenium installation:**
   ```bash
   python -c "from selenium import webdriver; print('Selenium OK')"
   ```

### If still no results

1. **Run debug script:**
   ```bash
   python debug_scraper.py
   ```
   This analyzes the website structure and saves:
   - `debug_response.html` - Raw page HTML
   - `debug_analysis.json` - Analysis results

2. **Check if website changed:**
   - Open https://www.naukri.com in browser
   - Right-click → Inspect → Check HTML structure
   - Look for CSS selectors containing "job", "card", "item"

### If timeout errors occur

Edit `naukri_selenium_scraper.py` and increase wait times:

```python
# Line ~60, change from:
wait = WebDriverWait(self.driver, 15)

# To:
wait = WebDriverWait(self.driver, 30)  # Longer wait
```

---

## 📊 Expected Output

After running Selenium scraper successfully, you'll get:

✓ `naukri_jobs.csv` - Jobs in spreadsheet format
✓ `naukri_jobs.json` - Jobs in JSON format  
✓ Console output showing job count

Example output:
```
===== NAUKRI JOB SCRAPING RESULTS =====
Total Jobs Found: 45

Job #1
  Title: Data Scientist - ML/AI
  Company: Google
  Experience: 8-12 years
  Location: Bangalore
  Salary: ₹25,00,000 - ₹45,00,000
  URL: https://www.naukri.com/jobs/...
```

---

## 📈 Performance Tips

| Factor | Impact | Solution |
|--------|--------|----------|
| First run | 5-10 min | Normal, includes page load |
| Subsequent runs | 3-5 min | Faster |
| Multiple locations | Longer | Run for one location first |
| Internet speed | Critical | Ensure stable connection |

---

## 🎯 Recommended Workflow

1. **First attempt:**
   ```bash
   python naukri_selenium_scraper.py
   ```

2. **If no results, debug:**
   ```bash
   python debug_scraper.py
   ```

3. **Review results:**
   ```bash
   python data_analyzer.py
   ```

4. **Export/Filter:**
   - Open `naukri_jobs.csv` in Excel
   - Sort by company, salary, posted date

---

## 🔐 Safety Notes

- ✓ Respectful 2-second delays between requests
- ✓ Standard browser user-agent
- ✓ Complies with web scraping best practices
- ✓ No sensitive data transmission

---

## 📞 Still Having Issues?

Check these files:
- `naukri_scraper.py` - Main scraper (basic)
- `naukri_selenium_scraper.py` - Advanced scraper (recommended)
- `config.py` - Configuration settings
- `debug_scraper.py` - Website structure analyzer

Edit `config.py` to customize:
```python
ROLES = ['Data Scientist', 'Python Developer']  # Change roles
EXPERIENCE = 11  # Change years
LOCATIONS = ['Bangalore', 'Chennai']  # Change locations
TARGET_COMPANIES = ['Google', 'Amazon']  # Change companies
```

---

## ✨ That's it!

The Selenium scraper should work. If you still get no results:
1. Run `debug_scraper.py` 
2. Check `debug_analysis.json`
3. Look at `debug_response.html` in a browser
4. Update CSS selectors based on current website structure

**Good luck! 🚀**
