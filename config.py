"""
Configuration file for Naukri Job Scraper
Modify these settings to customize your job search
"""

# Job Search Criteria
ROLES = [
    'Data Scientist',
    'Tableau Developer', 
    'Python Developer'
]

# Experience level (in years)
EXPERIENCE = 11

# Locations to search
LOCATIONS = [
    'Chennai',
    'Bangalore'
]

# Companies to filter (FAANG companies)
TARGET_COMPANIES = [
    'Google',
    'Amazon',
    'Meta',      # Facebook
    'Apple',
    'Netflix'
]

# Scraper Settings
REQUEST_TIMEOUT = 10  # seconds
DELAY_BETWEEN_REQUESTS = 2  # seconds

# Output Settings
OUTPUT_CSV_FILE = 'naukri_jobs.csv'
OUTPUT_JSON_FILE = 'naukri_jobs.json'

# Browser Settings (for Selenium scraper)
HEADLESS_BROWSER = True
BROWSER_TIMEOUT = 10  # seconds

# Logging Settings
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Additional FAANG Companies (if needed)
ADDITIONAL_COMPANIES = []
# Example: ['Flipkart', 'Swiggy', 'PhonePe']  # Indian unicorns

# Salary Range Filter (optional, set to None to disable)
MIN_SALARY = None
MAX_SALARY = None

# Custom Headers for HTTP requests
CUSTOM_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# API-like parameters for Naukri (if available)
# These are typically used in pagination
PAGE_SIZE = 50
MAX_PAGES = 10

# Filter Settings
FILTER_OPTIONS = {
    'job_type': None,  # 'full_time', 'part_time', 'contract', etc.
    'company_type': None,  # 'it', 'financial', 'startup', etc.
    'industry': None,  # Specific industry if needed
}

# Notification Settings (optional)
ENABLE_NOTIFICATIONS = False
NOTIFICATION_EMAIL = None

# Database Settings (optional, for storing results)
USE_DATABASE = False
DATABASE_FILE = 'jobs.db'

# Advanced Settings
VERIFY_SSL = True
USE_PROXY = False
PROXY_LIST = []  # Add proxy URLs if needed

# Data Export Options
EXPORT_FORMATS = ['csv', 'json']  # Can add 'excel', 'database'
COMBINE_RESULTS = True  # Combine results from multiple queries
