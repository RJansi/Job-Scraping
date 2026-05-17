# Complete Solution for Naukri.com Job Extraction

## Problem Analysis

Naukri.com uses **advanced JavaScript rendering with anti-scraping protections**, which makes automated scraping very challenging. Your options are:

---

## ✅ Solution 1: RECOMMENDED - Manual Browser + Export

### Fastest and Most Reliable Method

**Steps:**
1. Go to https://www.naukri.com/search
2. Enter your search criteria:
   - Keyword: **Data Scientist** (or Tableau Developer, Python Developer)
   - Location: **Bangalore** or **Chennai**
   - Experience: **11+**
3. Apply filters for FAANG companies if available
4. **Right-click → Inspect** on job listings
5. Copy all job data or take screenshots
6. Use our `data_analyzer.py` to process manually copied data

**Why this works:**
- ✅ 100% reliable
- ✅ No blocking risks
- ✅ Can see exactly what's filtered
- ✅ Takes 5-10 minutes for initial search

---

## ✅ Solution 2: Using Browser Extensions

### Recommended Browser Extensions:
1. **TableCapture** (Chrome) - Exports job listings to CSV
   - Download: https://chrome.google.com/webstore
   - Search: "Table Capture"

2. **Web Scraper** (Chrome) - Visual sitemap-based scraping
   - Download: https://chrome.google.com/webstore
   - Search: "Web Scraper"

3. **Data Scraper** (Chrome) - One-click table export
   - Download: https://chrome.google.com/webstore
   - Search: "Data Scraper"

**Steps:**
1. Install extension
2. Visit Naukri.com search results
3. Right-click → "Extract table" (or similar)
4. Export to CSV
5. Run: `python data_analyzer.py` on the exported file

---

## ✅ Solution 3: Using Excel Web Query (ADVANCED)

### For Advanced Users:

1. Open Excel
2. Data → From Web
3. Enter: `https://www.naukri.com/search?keyword=Data%20Scientist&location=Bangalore&experience=11`
4. Wait for page to load
5. Select job listings
6. Click Import

**Pros:** Built-in Excel functionality
**Cons:** May not work with all JavaScript content

---

## ✅ Solution 4: LinkedIn Alternative

### Switch to LinkedIn Jobs

Since Naukri has strong protections, consider LinkedIn:

```bash
# Create linkedin_scraper.py for LinkedIn job extraction
pip install linkedin-api
```

LinkedIn has more consistent data structure and may be easier to scrape.

---

## 📊 Solution 5: Manual Data Entry Helper

Use our prepared template to manually enter jobs found:

```python
# jobs_template.csv
Title,Company,Location,Experience,Salary,URL
Data Scientist - ML,Google,Bangalore,11+ years,₹30L,https://...
Tableau Developer,Amazon,Chennai,12+ years,₹25L,https://...
```

Then analyze with:
```bash
python data_analyzer.py
```

---

## 🚀 Automated Solution (FOR DEVELOPERS ONLY)

### Using Puppeteer (Node.js)

If you're willing to use Node.js instead:

```bash
npm install puppeteer axios cheerio
```

Create `scraper.js`:
```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://www.naukri.com/search', {
    waitUntil: 'networkidle2'
  });
  
  const jobs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('[data-job-id]')).map(job => ({
      title: job.querySelector('a.jobTitle')?.textContent,
      company: job.querySelector('.companyName')?.textContent,
      // ... extract more fields
    }));
  });
  
  console.log(JSON.stringify(jobs, null, 2));
  await browser.close();
})();
```

Run: `node scraper.js > jobs.json`

---

## 📋 Quick Comparison

| Method | Effort | Reliability | Time | Cost |
|--------|--------|-------------|------|------|
| Manual Browse | ⭐ Low | ⭐⭐⭐⭐⭐ 100% | 10 min | Free |
| Browser Extension | ⭐⭐ Low | ⭐⭐⭐⭐ 90% | 5 min | Free |
| Puppeteer (Node.js) | ⭐⭐⭐ Medium | ⭐⭐⭐ 70% | 10 min | Free |
| Paid Scraping Service | ⭐⭐⭐⭐ High | ⭐⭐⭐⭐ 85% | 2 min | $$ |
| Naukri API (if available) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Instant | May Need Auth |

---

## 🎯 RECOMMENDED IMMEDIATE ACTION

**DO THIS NOW:**

```bash
# Step 1: Open Naukri.com in your browser
https://www.naukri.com/search?keyword=Data%20Scientist&location=Bangalore&experience=11

# Step 2: Right-click job list → Inspect
# Step 3: Look for the HTML structure
# Step 4: Copy job data or take screenshots

# Step 5 (Optional): Create CSV template and run analyzer
python data_analyzer.py
```

---

## 📞 If Automated Scraping is Critical

### Use Paid Services:

1. **ScraperAPI** - Handles JavaScript rendering
   ```bash
   # pip install scraperapi-py
   ```

2. **Bright Data** - Rotating proxies + JavaScript rendering
   - Website: https://brightdata.com

3. **Apify** - Full scraping platform
   - Website: https://apify.com

These services cost $$ but guarantee results even against anti-scraping measures.

---

## 🛡️ Why Automated Scraping Fails

Naukri.com uses:
- ✗ CloudFlare protection
- ✗ JavaScript rendering (dynamic content)
- ✗ User-agent detection
- ✗ Rate limiting
- ✗ Session-based access
- ✗ Anti-bot measures

These are specifically designed to block automated scrapers.

---

## ✨ Next Steps

### IMMEDIATE (Recommended):
1. Manually search on Naukri.com
2. Export results using browser extension
3. Run analyzer on exported data

### IF YOU NEED FULLY AUTOMATED:
1. Try Puppeteer (Node.js) approach
2. Or use paid scraping service
3. Or wait for Naukri API documentation

### FOR DATA ANALYSIS:
```bash
# Once you have job data in CSV
python data_analyzer.py
```

---

## 📄 Sample CSV Template

Create `manual_jobs.csv`:
```
timestamp,role,location,title,company,experience,salary,job_url
2026-05-13,Data Scientist,Bangalore,Data Scientist - ML,Google,8-12 years,₹30,00,000,https://www.naukri.com/...
2026-05-13,Data Scientist,Bangalore,Senior Data Scientist,Amazon,10+ years,₹28,00,000,https://www.naukri.com/...
2026-05-13,Python Developer,Chennai,Python Backend Engineer,Google,11 years,₹25,00,000,https://www.naukri.com/...
```

Then analyze:
```bash
python data_analyzer.py  # It will read the CSV
```

---

## 🎓 Learning Resources

- Puppeteer: https://pptr.dev/
- Cheerio (Node.js HTML parsing): https://cheerio.js.org/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
- Selenium: https://www.selenium.dev/

---

**Need help? Use any of the solutions above. The manual browser method is quickest! 🚀**
