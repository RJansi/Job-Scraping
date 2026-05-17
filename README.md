# Naukri.com Job Scraper

A Python-based web scraper to extract job listings from Naukri.com with specific filters for Data Science, Tableau Development, and Python Development roles.

## Features

- **Multiple Scraping Methods**:
  - `naukri_scraper.py`: Basic HTTP scraper using BeautifulSoup
  - `naukri_selenium_scraper.py`: Advanced Selenium-based scraper for JavaScript-rendered content

- **Filter Options**:
  - Job Roles: Data Scientist, Tableau Developer, Python Developer
  - Experience: 11+ years
  - Locations: Chennai, Bangalore
  - Companies: FAANG (Google, Amazon, Meta, Apple, Netflix)

- **Output Formats**:
  - CSV files (`naukri_jobs.csv`, `naukri_jobs_selenium.csv`)
  - JSON files (`naukri_jobs.json`, `naukri_jobs_selenium.json`)
  - Console display with formatted output

- **Data Extracted**:
  - Job Title
  - Company Name
  - Experience Required
  - Location
  - Salary Range
  - Posted Date
  - Skills Required
  - Job Description Snippet
  - Job URL

## Installation

1. Ensure Python 3.8+ is installed
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Scraper (Recommended for Initial Use)
```bash
python naukri_scraper.py
```

### Advanced Selenium Scraper
```bash
python naukri_selenium_scraper.py
```

## Requirements

- requests>=2.31.0
- beautifulsoup4>=4.12.0
- lxml>=4.9.0
- selenium>=4.15.0 (for Selenium scraper)
- pandas>=2.0.0 (optional, for data analysis)

## Output Files

- `naukri_jobs.csv` / `naukri_jobs.json` - Results from basic scraper
- `naukri_jobs_selenium.csv` / `naukri_jobs_selenium.json` - Results from Selenium scraper

## Customization

Edit the scraper configuration in the respective Python files:

```python
self.roles = ['Data Scientist', 'Tableau Developer', 'Python Developer']
self.experience = 11
self.locations = ['Chennai', 'Bangalore']
self.companies = ['Google', 'Amazon', 'Meta', 'Apple', 'Netflix']
```

## Notes

- Respectful delays (2 seconds) are implemented between requests to avoid overwhelming the server
- User-Agent headers are used to mimic legitimate browser access
- The Selenium scraper provides better handling of JavaScript-rendered content
- FAANG filtering is automatically applied to results
- Logging provides real-time feedback on the scraping process

## Legal Notice

Please ensure you comply with Naukri.com's Terms of Service and robots.txt before running this scraper. Web scraping should be done responsibly and ethically.

## Troubleshooting

### No jobs found
- Check your internet connection
- Verify the website structure hasn't changed
- Try the Selenium scraper instead
- Check the console logs for error messages

### Selenium WebDriver not found
- Download ChromeDriver from: https://chromedriver.chromium.org/
- Place it in your system PATH or specify the path in the code

### Request timeout
- Increase the timeout value in the code
- Check your internet connection speed
- Try again later if the website is slow

## Author

Job Hunt Agent - Web Scraping Tool
